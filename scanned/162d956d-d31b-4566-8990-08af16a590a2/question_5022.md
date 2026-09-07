# Q5022: Migrated zec.omft.near: the same token id with different letter 

## Question
For migrated PoA token `nep141:zec.omft.near`, when the same token id with different letter case, can an unprivileged caller make the SDK route the withdrawal through a bridge other than Omni or to a chain other than `zec`, because `POA_TOKENS_MIGRATED_TO_OMNI_BRIDGE[contractId]` is an exact-key lookup while `validateNearAddress` lowercases nothing, sending tokens to a `receiver_id` that does not hold them?

## Target
- File/function: packages/intents-sdk/src/constants/poa-tokens-migrated-to-omni-bridge.ts; poa-bridge.ts `supports`; omni-bridge.ts `supports`, `makeAssetInfo`, `isPoaTokenMigratedToOmniBridge`
- Entrypoint: `IntentsSDK.processWithdrawal` / `createWithdrawalIntents` / `parseAssetId`
- Attacker controls: `assetId` = `nep141:zec.omft.near`, `routeConfig`
- Exploit idea: `POA_TOKENS_MIGRATED_TO_OMNI_BRIDGE[contractId]` is an exact-key lookup while `validateNearAddress` lowercases nothing
- Invariant to test: Every withdrawal of `zec.omft.near` must produce an `ft_withdraw` to `omni.bridge.near` with `recipient` on its migrated origin chain, regardless of routeConfig; anything else must throw.
- Expected Immunefi impact: Critical - funds delivered to a wrong address/chain/contract with no recovery (HackenProof: cross-chain address validation / withdrawal processing; Immunefi class: direct theft or permanent loss of user funds)
- Fast validation: vitest: iterate all bridges' `supports()` for this id under each routeConfig and assert only OmniBridge accepts with the expected ChainKind.
