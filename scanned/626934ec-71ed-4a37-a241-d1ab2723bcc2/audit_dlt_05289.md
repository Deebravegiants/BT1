# [?] fix(ln): do not panic on a preimage status query for an outgoing contract

## Summary
Severity: Unknown
Chain: Fedimint
Component: fedimint/fedimint
Published: 2026-08-06
Source: https://github.com/fedimint/fedimint/commit/52e4ccde4f69cc62700c34d591acbc8b822ee885
Type: security-commit

## Details
fix(ln): do not panic on a preimage status query for an outgoing contract

`GET_DECRYPTED_PREIMAGE_STATUS` is a public, unauthenticated endpoint. It
resolves the contract with `wait_key_exists(ContractKey(id))`, and
`ContractKey` holds either contract variant, so the caller picks which
variant the handler ends up with. `get_incoming_contract_account` then
hit an unconditional `panic!("Contract is not an IncomingContractAccount")`
for anything that is not incoming.

`process_output` applies no validation at all to `Contract::Outgoing`, so
an attacker funds their own outgoing contract for one msat, calls the
endpoint with its id, and the handler panics. Over iroh that takes the
guardian process down.

Make `get_incoming_contract_account` return an `Option` and have the
endpoint answer a 400 for a non-incoming contract.

The sibling `AWAIT_PREIMAGE_DECRYPTION` was not affected and is left
functionally unchanged: it uses `wait_value_matches`, whose predicate
returns `false` for `FundedContract::Outgoing`, so it simply keeps
waiting rather than resolving to a contract of the wrong variant. Its
call site now carries an `expect` naming that invariant instead of
relying on a panic several frames away.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_011hiuVTowKNSSYVtxwQTdP9
