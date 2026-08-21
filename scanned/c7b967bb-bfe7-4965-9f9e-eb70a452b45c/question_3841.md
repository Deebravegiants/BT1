# Q3841: Agent restart in set_next_objective loses accumulated security state (biometric_capture/mod.rs)

## Question
Can an unprivileged attacker crash or stall the inference agent behind `set_next_objective` in [src/plans/biometric_capture/mod.rs](src/plans/biometric_capture/mod.rs) (adversarial input, resource pressure), so its restart resets accumulated fraud/quality evidence while the signup continues with a clean slate?

## Target
- File/function: [src/plans/biometric_capture/mod.rs](src/plans/biometric_capture/mod.rs) -> `set_next_objective` (function)
- Entrypoint: Scene input that reliably crashes or stalls the agent
- Attacker controls: the adversarial input and its timing within the capture window
- Exploit idea: Check what `set_next_objective` does with a restarted agent: does it abort the signup or resume with empty state?
- Invariant to test: Agent restart during a session invalidates the session, never silently resets its evidence.
- Expected Immunefi impact: Anti-fraud evidence erased mid-signup by an attacker-induced restart
- Fast validation: Fault-injection test restarting the agent mid-capture and asserting session abort.
