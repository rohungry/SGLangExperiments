#<h1 align="center">Instructions for how to setup llama3.2-1B-Instruct modal on an A10 GPU on Modal (on-demand GPU service)</h1>

1. Install Modal and sign-up - go to www.modal.com.
2. Go to hugging face, and follow the instructions to get access to the model llama3.2-1B-Instruct.
3. Setup access token on hugging face for the model - look up instructions on how to do this.  
4. Setup the modal secret with your hugging face token - this will allow modal to pull the model weights and graph inside of the A10 GPU container:

'modal secret create huggingface-secret HF_TOKEN=hf_yourNewTokenHere'

5. Run 'modal deploy test_modal_server_llama3.2-1B-Instruct.py' on a local terminal to get an SGLang server running in an A10 GPU container on Modal.

After this completes, you can test the endpoint with curl on a terminal. For example (replace the url with your server url - go to the app inside modal and copy the url in the app pane):

curl https://rohunkshirsagar--llama-sglang-test-serve.modal.run/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "meta-llama/Llama-3.2-1B-Instruct",
    "messages": [
      {"role": "user", "content": "Write a haiku about a dog."}                                 
    ],
    "temperature": 0.2,
    "max_tokens": 60
  }'


6. Install OpenAI client API.  Create a virtual environment with uv (the preferred way in the python community today) OR use the usual python .venv syntax to setup a virtual environment, and then run: 'uv venv && source .venv/bin/activate && uv pip install openai'.

Alternatively, you can use the usual python virtual environment aka venv approach in a terminal:

python3 -m venv .venv
source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install openai

7. You can test this in a terminal by running 'python test_modal_local_client_llama3.2-1B-Instruct.py'.   You should now have a multi-turn llama3.2-1B-Instruct chatbot running on modal on the endpoint below, with prompt access via the terminal.  Here is an example of how to use it from the terminal:

you: Write a haiku about a dog.

(posts to endpont) 

assistant:

Furry ball of joy

Tail wags with happy delight

Faithful canine friend

----
That worked! Here is some log information you can see on Modal:

Apr 19 at 15:43:46.039
[2026-04-19 22:43:46] Prefill batch, #new-seq: 1, #new-token: 1, #cached-token: 42, token usage: 0.00, #running-req: 0, #queue-req: 0, cuda graph: True, input throughput (token/s): 0.03
Apr 19 at 15:43:46.152
[2026-04-19 22:43:46] INFO:     172.20.52.20:16262 - "POST /v1/chat/completions HTTP/1.1" 200 OK
Apr 19 at 15:43:46.203
   POST /v1/chat/completions -> 200 OK  (duration: 261.2 ms, execution: 177.7 ms)
