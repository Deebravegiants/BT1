# Q1735: Agent restart in serialized_mask loses accumulated security state (iris/types.rs)

## Question
Can an unprivileged attacker crash or stall the inference agent behind `serialized_mask` in [src/agents/python/iris/types.rs](src/agents/python/iris/types.rs) (adversarial input, resource pressure), so its restart resets accumulated fraud/quality evidence while the signup continues with a clean slate?

## Target
- File/function: [src/agents/python/iris/types.rs](src/agents/python/iris/types.rs) -> `serialized_mask` (function)
- Entrypoint: Scene input that reliably crashes or stalls the agent
- Attacker controls: the adversarial input and its timing within the capture window
- Exploit idea: Check what `serialized_mask` does with a restarted agent: does it abort the signup or resume with empty state?
- Invariant to test: Agent restart during a session invalidates the session, never silently resets its evidence.
- Expected Immunefi impact: Anti-fraud evidence erased mid-signup by an attacker-induced restart
- Fast validation: Fault-injection test restarting the agent mid-capture and asserting session abort.
