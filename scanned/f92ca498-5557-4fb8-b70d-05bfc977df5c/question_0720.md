# Q0720: unpack-u16 via liquidate-multi: destroy value through a truncation the opposite operation 

## Question
Does `liquidate-multi` (mainnet/contracts/market/v0-4-market.clar:1593) let an unprivileged attacker who controls the trait principals supplied per entry reach `unpack-u16` (mainnet/contracts/vault/v0-vault-stx.clar:259) in a state where it destroy value through a truncation the opposite operation does not restore? Given that it unpacks eight u16 curve fields from one packed word, the invariant that every round-up has a paired round-down that repetition cannot exploit breaks and the result is temporary freezing of funds.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:259` -> `unpack-u16`
- Entrypoint: `liquidate-multi` (`mainnet/contracts/market/v0-4-market.clar:1593`), unprivileged and publicly callable
- Attacker controls: the trait principals supplied per entry
- Exploit idea: `unpack-u16` unpacks eight u16 curve fields from one packed word. Reach it through `liquidate-multi` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: High - temporary freezing of funds
- Fast validation: Fuzz the trait principals supplied per entry across its boundary values through `liquidate-multi` in simnet and assert `unpack-u16` never returns a value that breaks the invariant.
