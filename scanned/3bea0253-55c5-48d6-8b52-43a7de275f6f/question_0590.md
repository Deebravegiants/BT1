# Q0590: Agent restart in extract_option_rkyv_ndarray_d3 loses accumulated security state (face_identifier/types.rs)

## Question
Can an unprivileged attacker crash or stall the inference agent behind `extract_option_rkyv_ndarray_d3` in [src/agents/python/face_identifier/types.rs](src/agents/python/face_identifier/types.rs) (adversarial input, resource pressure), so its restart resets accumulated fraud/quality evidence while the signup continues with a clean slate?

## Target
- File/function: [src/agents/python/face_identifier/types.rs](src/agents/python/face_identifier/types.rs) -> `extract_option_rkyv_ndarray_d3` (function)
- Entrypoint: Scene input that reliably crashes or stalls the agent
- Attacker controls: the adversarial input and its timing within the capture window
- Exploit idea: Check what `extract_option_rkyv_ndarray_d3` does with a restarted agent: does it abort the signup or resume with empty state?
- Invariant to test: Agent restart during a session invalidates the session, never silently resets its evidence.
- Expected Immunefi impact: Anti-fraud evidence erased mid-signup by an attacker-induced restart
- Fast validation: Fault-injection test restarting the agent mid-capture and asserting session abort.
