# Q1137: remove_code can collide or mis-bind contract addresses

## Question
Can an unprivileged attacker use `remove_code` so two different semantic creations or account mappings resolve to the same effective address or fallback identity?

## Target
- File/function: substrate/frame/contracts/src/lib.rs::remove_code
- Entrypoint: public VM / contract execution extrinsic `remove_code`
- Attacker controls: IDs, hashes, nonces, or location fields
- Exploit idea: Probe salts, caller identity, fallback mapping, and eth/substrate bridging assumptions.
- Invariant to test: Every deployed or mapped contract or account identity must be unique and bound to exactly one owner context.
- Expected Immunefi impact: Unauthorized code/call execution or theft from contract-controlled funds
- Fast validation: Try repeated instantiation or mapping with same and near-colliding inputs and then exercise authorization-sensitive follow-up calls.
