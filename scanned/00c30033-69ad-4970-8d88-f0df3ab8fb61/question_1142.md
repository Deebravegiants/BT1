# Q1142: Backpressure/queue policy in no_state drops security-relevant data (orb-relay-client/client.rs)

## Question
Can an unprivileged attacker saturate the channel handled by `no_state` in [orb-relay-client/src/client.rs](orb-relay-client/src/client.rs) so security-relevant messages (fraud verdicts, quality failures) are dropped by the overflow policy while permissive ones survive?

## Target
- File/function: [orb-relay-client/src/client.rs](orb-relay-client/src/client.rs) -> `no_state` (function)
- Entrypoint: Scene/scan input driving maximum message rate
- Attacker controls: the message rate and mix produced by the scene
- Exploit idea: Check the drop policy in `no_state`: does it distinguish mandatory from best-effort messages?
- Invariant to test: Mandatory security messages are never dropped by backpressure; saturation fails the session.
- Expected Immunefi impact: Anti-fraud verdict lost to attacker-induced saturation
- Fast validation: Load test on `no_state` asserting mandatory messages are delivered or the session aborts.
