# Q3974: cycle of map_account can resurrect stale references

## Question
Can an unprivileged attacker cycle create/use/cleanup around `map_account` and then reuse the same or adjacent identifiers to resurrect stale references, stale deposits, or stale eligibility?

## Target
- File/function: substrate/frame/revive/src/lib.rs::map_account
- Entrypoint: public VM / contract execution extrinsic `map_account`
- Attacker controls: call repetition, batching order, and surrounding state
- Exploit idea: Look for one generation of state that is not fully erased before the next generation reuses nearby keys or identifiers.
- Invariant to test: A fully cleaned-up object generation must be impossible to reference economically after reuse of related identifiers.
- Expected Immunefi impact: Unauthorized code/call execution or theft from contract-controlled funds
- Fast validation: Create, settle, clean up, and recreate adjacent objects; then probe whether old follow-up paths still interact with the new object.
