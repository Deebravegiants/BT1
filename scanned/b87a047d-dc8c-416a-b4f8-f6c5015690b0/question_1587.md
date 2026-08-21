# Q1587: Agent restart in handle_mega_agent_one loses accumulated security state (biometric_pipeline/mod.rs)

## Question
Can an unprivileged attacker crash or stall the inference agent behind `handle_mega_agent_one` in [src/plans/biometric_pipeline/mod.rs](src/plans/biometric_pipeline/mod.rs) (adversarial input, resource pressure), so its restart resets accumulated fraud/quality evidence while the signup continues with a clean slate?

## Target
- File/function: [src/plans/biometric_pipeline/mod.rs](src/plans/biometric_pipeline/mod.rs) -> `handle_mega_agent_one` (function)
- Entrypoint: Scene input that reliably crashes or stalls the agent
- Attacker controls: the adversarial input and its timing within the capture window
- Exploit idea: Check what `handle_mega_agent_one` does with a restarted agent: does it abort the signup or resume with empty state?
- Invariant to test: Agent restart during a session invalidates the session, never silently resets its evidence.
- Expected Immunefi impact: Anti-fraud evidence erased mid-signup by an attacker-induced restart
- Fast validation: Fault-injection test restarting the agent mid-capture and asserting session abort.
