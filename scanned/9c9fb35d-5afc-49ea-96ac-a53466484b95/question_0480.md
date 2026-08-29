# Q0480: resolve-dia via liquidate-multi: destroy value through a truncation the opposite operation 

## Question
Does `liquidate-multi` (mainnet/contracts/market/v0-4-market.clar:1593) let an unprivileged attacker who controls the trait principals supplied per entry reach `resolve-dia` (mainnet/contracts/market/v0-4-market.clar:326) in a state where it destroy value through a truncation the opposite operation does not restore? Given that it derives a (string-ascii 32) key from a (buff 32) ident, the invariant that every round-up has a paired round-down that repetition cannot exploit breaks and the result is permanent freezing of funds.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:326` -> `resolve-dia`
- Entrypoint: `liquidate-multi` (`mainnet/contracts/market/v0-4-market.clar:1593`), unprivileged and publicly callable
- Attacker controls: the trait principals supplied per entry
- Exploit idea: `resolve-dia` derives a (string-ascii 32) key from a (buff 32) ident. Reach it through `liquidate-multi` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Fuzz the trait principals supplied per entry across its boundary values through `liquidate-multi` in simnet and assert `resolve-dia` never returns a value that breaks the invariant.
