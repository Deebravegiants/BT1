# Q5393: call-liquidate via liquidate-multi: leave a residue that no reconciliation pass ever inspects

## Question
Can an unprivileged attacker entering through `liquidate-multi` (mainnet/contracts/market/v0-4-market.clar:1593), controlling how many entries share one price snapshot (price-feeds is passed as none), drive `call-liquidate` (mainnet/contracts/market/v0-4-market.clar:907) — which invokes `liquidate` with `none` for price-feeds, so a whole batch shares one snapshot — to leave a residue that no reconciliation pass ever inspects, breaking the invariant that every round-up has a paired round-down that repetition cannot exploit, and cause protocol insolvency?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:907` -> `call-liquidate`
- Entrypoint: `liquidate-multi` (`mainnet/contracts/market/v0-4-market.clar:1593`), unprivileged and publicly callable
- Attacker controls: how many entries share one price snapshot (price-feeds is passed as none)
- Exploit idea: `call-liquidate` invokes `liquidate` with `none` for price-feeds, so a whole batch shares one snapshot. Reach it through `liquidate-multi` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Run the baseline `liquidate-multi` call, then the attacker-shaped one with how many entries share one price snapshot (price-feeds is passed as none), and assert the attacker's net token balance change is zero or negative.
