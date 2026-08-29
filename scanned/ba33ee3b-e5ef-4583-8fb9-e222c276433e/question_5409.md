# Q5409: receive-underlying via liquidate-redeem: leave a residue that no reconciliation pass ever inspects

## Question
Can an unprivileged attacker entering through `liquidate-redeem` (mainnet/contracts/market/v0-4-market.clar:1604), controlling the redemption receiver, drive `receive-underlying` (mainnet/contracts/vault/v0-vault-stx.clar:291) — which pulls the underlying from a named account — to leave a residue that no reconciliation pass ever inspects, breaking the invariant that every round-up has a paired round-down that repetition cannot exploit, and cause temporary freezing of funds?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:291` -> `receive-underlying`
- Entrypoint: `liquidate-redeem` (`mainnet/contracts/market/v0-4-market.clar:1604`), unprivileged and publicly callable
- Attacker controls: the redemption receiver
- Exploit idea: `receive-underlying` pulls the underlying from a named account. Reach it through `liquidate-redeem` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: High - temporary freezing of funds
- Fast validation: Snapshot every state variable `receive-underlying` touches, run `liquidate-redeem` with the redemption receiver, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
