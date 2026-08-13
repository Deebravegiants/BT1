# Q1961: utils restore-time auth gap via getUniqueTagForWalletAccount

## Question
Can an unprivileged attacker use wallet create/import/unlock/restore flow reachable from normal app usage with attacker-controlled `name`, `port`, and transition timing so that `getUniqueTagForWalletAccount` in `features/wallet-accounts/src/module/utils.ts` make old unlocked material, old seed state, or old account scope survive a lifecycle transition that should clear it, violating the rule that fallback authentication must not weaken the lock or approval policy enforced by the normal path, and ultimately reaching `Private key or private key generation leakage leading to unauthorized access to user funds`?

## Target
- File/function: features/wallet-accounts/src/module/utils.ts::getUniqueTagForWalletAccount
- Entrypoint: wallet create/import/unlock/restore flow reachable from normal app usage
- Attacker controls: wallet-account selection, lifecycle hooks, and repeated start/load cycles
- Exploit idea: make old unlocked material, old seed state, or old account scope survive a lifecycle transition that should clear it
- Invariant to test: fallback authentication must not weaken the lock or approval policy enforced by the normal path
- Expected Immunefi impact: Private key or private key generation leakage leading to unauthorized access to user funds
- Fast validation: restore crafted state across multiple wallet accounts and assert only the intended seed/account pair is mutated or exposed
