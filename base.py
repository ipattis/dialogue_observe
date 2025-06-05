import requests
import json
import time
import asyncio
import aiohttp
from typing import List, Dict, Optional

class ModelClient:
    def __init__(self, name: str, model_name: str, system_prompt: str = ""):
        self.name = name
        self.model_name = model_name
        self.system_prompt = system_prompt
        self.conversation_history = []
        
    async def generate_response(self, session: aiohttp.ClientSession, prompt: str, 
                              base_url: str, temperature: float = 0.7, max_tokens: int = 500) -> str:
        """Generate a response from the model"""
        messages = []
        
        # Add system prompt if provided
        if self.system_prompt:
            messages.append({"role": "system", "content": self.system_prompt})
            
        # Add conversation history
        messages.extend(self.conversation_history)
        
        # Add current prompt
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": self.model_name,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False
        }
        
        try:
            async with session.post(f"{base_url}/v1/chat/completions", 
                                  json=payload, 
                                  headers={"Content-Type": "application/json"}) as response:
                if response.status == 200:
                    result = await response.json()
                    assistant_response = result["choices"][0]["message"]["content"]
                    
                    # Update conversation history
                    self.conversation_history.append({"role": "user", "content": prompt})
                    self.conversation_history.append({"role": "assistant", "content": assistant_response})
                    
                    # Keep history manageable (last 10 exchanges)
                    if len(self.conversation_history) > 20:
                        self.conversation_history = self.conversation_history[-20:]
                    
                    return assistant_response
                else:
                    return f"Error: HTTP {response.status}"
        except Exception as e:
            return f"Error: {str(e)}"

class DialogueOrchestrator:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.models = {}
        self.dialogue_history = []
        
    def add_model(self, role: str, client: ModelClient):
        """Add a model to the orchestrator"""
        self.models[role] = client
        
    async def run_dialogue(self, initial_topic: str, rounds: int = 5, 
                          commentary_frequency: int = 2):
        """Run the dialogue between models with commentary"""
        print(f"🎭 Starting dialogue on topic: {initial_topic}\n")
        print("=" * 60)
        
        async with aiohttp.ClientSession() as session:
            # Initialize the conversation
            current_prompt = initial_topic
            
            for round_num in range(rounds):
                print(f"\n🔄 Round {round_num + 1}")
                print("-" * 40)
                
                # Model A responds
                print(f"🤖 {self.models['model_a'].name}:")
                response_a = await self.models['model_a'].generate_response(
                    session, current_prompt, self.base_url
                )
                print(f"{response_a}\n")
                self.dialogue_history.append({
                    "round": round_num + 1,
                    "speaker": "model_a",
                    "content": response_a
                })
                
                # Model B responds to A's response
                print(f"🤖 {self.models['model_b'].name}:")
                response_b = await self.models['model_b'].generate_response(
                    session, response_a, self.base_url
                )
                print(f"{response_b}\n")
                self.dialogue_history.append({
                    "round": round_num + 1,
                    "speaker": "model_b", 
                    "content": response_b
                })
                
                # Commentary model provides analysis
                if (round_num + 1) % commentary_frequency == 0:
                    print(f"💬 {self.models['commentator'].name} Commentary:")
                    
                    # Prepare context for commentator
                    recent_exchange = f"""
                    Recent exchange:
                    {self.models['model_a'].name}: {response_a}
                    
                    {self.models['model_b'].name}: {response_b}
                    
                    Please provide commentary on this exchange, analyzing the dialogue quality, 
                    key points, areas of agreement/disagreement, and interesting developments.
                    """
                    
                    commentary = await self.models['commentator'].generate_response(
                        session, recent_exchange, self.base_url
                    )
                    print(f"📝 {commentary}\n")
                    print("=" * 60)
                
                # Set up next round's prompt
                current_prompt = response_b
                
                # Add a small delay to avoid overwhelming the APIs
                await asyncio.sleep(1)
        
        # Final comprehensive commentary
        print(f"\n🎯 Final Commentary from {self.models['commentator'].name}:")
        print("=" * 60)
        
        final_summary = f"""
        Please provide a comprehensive analysis of the entire dialogue between 
        {self.models['model_a'].name} and {self.models['model_b'].name} on the topic: {initial_topic}
        
        Key aspects to analyze:
        - Overall dialogue quality and coherence
        - Main themes and arguments presented
        - Evolution of the discussion
        - Notable insights or interesting points
        - Areas where the models complemented or challenged each other
        """
        
        async with aiohttp.ClientSession() as session:
            final_commentary = await self.models['commentator'].generate_response(
                session, final_summary, self.base_url
            )
            print(final_commentary)

# Example usage and configuration
async def main():
    # Configure your single LM Studio endpoint
    base_url = "http://10.226.10.31:1234"  # Your LM Studio server
    orchestrator = DialogueOrchestrator(base_url)
    
    # Model A - Creative/Philosophical
    model_a = ModelClient(
        name="Philosopher",
        model_name="qwen3-30b-a3b",  # Your first model
        system_prompt="""You are a thoughtful philosopher who enjoys deep discussions. 
        You ask probing questions and explore ideas from multiple angles. 
        Keep responses conversational and engaging, around 100-200 words."""
    )
    
    # Model B - Analytical/Scientific  
    model_b = ModelClient(
        name="Analyst",
        model_name="gemma-3-27b-it-qat",  # Your second model
        system_prompt="""You are an analytical thinker who values evidence and logic. 
        You provide structured reasoning and like to examine assumptions. 
        Keep responses clear and well-reasoned, around 100-200 words."""
    )
    
    # Commentary Model
    commentator = ModelClient(
        name="Observer",
        model_name="deepseek-r1-distill-qwen-7b",  # Your third model (example name)
        system_prompt="""You are an insightful observer who analyzes conversations. 
        Provide thoughtful commentary on dialogue quality, key insights, and interesting dynamics. 
        Be constructive and highlight both strengths and areas for improvement."""
    )
    
    # Add models to orchestrator
    orchestrator.add_model("model_a", model_a)
    orchestrator.add_model("model_b", model_b)
    orchestrator.add_model("commentator", commentator)
    
    # Start the dialogue
    topic = "What role should artificial intelligence play in creative endeavors?"
    await orchestrator.run_dialogue(topic, rounds=6, commentary_frequency=2)

if __name__ == "__main__":
    # Install required packages first:
    # pip install aiohttp requests
    
    print("Three-Model Dialogue System")
    print("Make sure you have multiple models loaded in LM Studio!")
    print("Update the model names in the main() function before running.\n")
    
    asyncio.run(main())