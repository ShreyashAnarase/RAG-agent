
start-api:
	tmux new-session -d -s fastapi "source .venv/bin/activate && uvicorn main:app --reload"

start-chunker:
	tmux new-session -d -s chunker "source .venv/bin/activate && python chunking_worker.py"

start-embedder:
	tmux new-session -d -s embedder "source .venv/bin/activate && python embedding_worker.py"

# attach to the one whose o/p needed to see , can switch
tmux attach -t fastapi  # or chunker/embedder

# ADD COMMNAD TO START KAFKA BROKER 
start kafka-broker:

# Start all components 
start-all: start-api start-chunker start-embedder
	tmux list-sessions

# Stop all tmux sessions
stop-all:
	tmux kill-server
