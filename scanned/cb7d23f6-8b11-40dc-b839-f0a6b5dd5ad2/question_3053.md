# Q3053: omniAddress Arbitrum: an address with leading zeros stripped (

## Question
For Omni withdrawals to Arbitrum, `deriveOmniWithdrawIntentParams` lowercases only `/^bc1/i` BTC addresses and otherwise passes `destinationAddress` verbatim into `omniAddress(ChainKind, address)` and into `calculateStorageAccountId` (where letter case changes the derived storage account). With an address with leading zeros stripped (short form), can an unprivileged user produce a `recipient` the Omni connector rejects or maps to a different account, and a `storage_deposit` paid to a storage account that never gets used, so the native fee is lost and the token transfer is refunded to intents.near rather than the user?

## Target
- File/function: packages/intents-sdk/src/bridges/omni-bridge/omni-withdraw-params.ts `deriveOmniWithdrawIntentParams` (destinationAddress case handling, calculateStorageAccountId); omni-bridge-utils.ts `createWithdrawIntentsPrimitive`
- Entrypoint: `IntentsSDK.processWithdrawal` / `createWithdrawalIntents` (Omni)
- Attacker controls: `destinationAddress` textual form for Arbitrum
- Exploit idea: Case/prefix normalisation is chain-specific and only implemented for BTC bech32; storage account derivation is case-sensitive.
- Invariant to test: recipient encoded == canonical address the connector credits; storage account derived from the same recipient the transfer uses.
- Expected Immunefi impact: High - withdrawal stuck or refunded to the wrong account until manual intervention (HackenProof: withdrawal processing; Immunefi class: temporary freezing of funds)
- Fast validation: vitest: call `deriveOmniWithdrawIntentParams` with variant casings and assert `recipient` and `storageDepositAccountId` stability.
