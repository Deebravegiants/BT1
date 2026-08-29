# [?] fix: fixed race condition on vault creation and get seedphrase (#44276)

## Summary
Severity: Unknown
Chain: MetaMask
Component: MetaMask/metamask-extension
Published: 2026-07-13
Source: https://github.com/MetaMask/metamask-extension/commit/e9d9c6cd75085859e8702f945e43f7f1dd793a9d
Type: security-commit

## Details
fix: fixed race condition on vault creation and get seedphrase (#44276)

## **Description**

### Context

Fixes
[#44068](https://github.com/MetaMask/metamask-extension/issues/44068) —
an intermittent E2E failure in `reset-wallet.spec.ts` during the
**second** onboarding pass after wallet reset. The failure surfaces as:

```
OnboardingFlow: failed to create new account Error: Keyring not found
Error creating password Error: Keyring not found
```

`Keyring not found` is thrown from
`KeyringController.exportSeedPhrase()` when the HD keyring has been
cleared from memory mid-export (`keyrings[0]?.keyring` is falsy). On the
create-wallet path this happens via `createNewVaultAndGetSeedPhrase` →
`getSeedPhrase` → `exportSeedPhrase`.

### Root cause (confirmed)

This was **reproduced locally** with the same error signature as CI.

MetaMask can have **multiple UI surfaces** open at once (main window +
side panel). They share one background, but each has its **own Redux
store**.

On second-pass onboarding password submit, the main window:

1. `createNewVault` — creates the vault and unlocks it
2. `getSeedPhrase` — exports the recovery phrase

Previously these were **two separate background RPCs** with
`createVaultMutex` released between them. Meanwhile, a **stale side
panel** (left open after first onboarding) could react to `isUnlocked:

_Trimmed to 38 lines — full report: https://github.com/MetaMask/metamask-extension/commit/e9d9c6cd75085859e8702f945e43f7f1dd793a9d_
