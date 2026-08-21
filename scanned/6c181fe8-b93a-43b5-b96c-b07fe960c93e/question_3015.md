# Q3015: Agent restart in Input loses accumulated security state (python/mega_agent_two.rs)

## Question
Can an unprivileged attacker crash or stall the inference agent behind `Input` in [src/agents/python/mega_agent_two.rs](src/agents/python/mega_agent_two.rs) (adversarial input, resource pressure), so its restart resets accumulated fraud/quality evidence while the signup continues with a clean slate?

## Target
- File/function: [src/agents/python/mega_agent_two.rs](src/agents/python/mega_agent_two.rs) -> `Input` (type)
- Entrypoint: Scene input that reliably crashes or stalls the agent
- Attacker controls: the adversarial input and its timing within the capture window
- Exploit idea: Check what `Input` does with a restarted agent: does it abort the signup or resume with empty state?
- Invariant to test: Agent restart during a session invalidates the session, never silently resets its evidence.
- Expected Immunefi impact: Anti-fraud evidence erased mid-signup by an attacker-induced restart
- Fast validation: Fault-injection test restarting the agent mid-capture and asserting session abort.
