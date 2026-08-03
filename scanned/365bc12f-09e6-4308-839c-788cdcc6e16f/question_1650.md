# Q1650: remove_code nested runtime call path can bypass final call checks

## Question
Can an unprivileged attacker use `remove_code` to wrap a runtime call that passes one layer's validation but executes with broader semantics in the final layer?

## Target
- File/function: substrate/frame/contracts/src/lib.rs::remove_code
- Entrypoint: public VM / contract execution extrinsic `remove_code`
- Attacker controls: IDs, hashes, nonces, or location fields
- Exploit idea: Focus on eth-substrate bridging, fallback dispatch, or nested call wrappers whose validation and execution contexts differ.
- Invariant to test: The final executed nested call must obey the exact authorization and charging assumptions made by the outer entrypoint.
- Expected Immunefi impact: Unauthorized code/call execution or theft from contract-controlled funds
- Fast validation: Attempt the most sensitive nested public call reachable through the wrapper and compare direct vs wrapped execution semantics.
