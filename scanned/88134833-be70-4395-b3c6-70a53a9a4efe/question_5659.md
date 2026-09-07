# Q5659: Migrated sol-df27d7abcc1c656d4ac3b1399b: `createPoaBridgeRoute()` is passed expli

## Question
For migrated PoA token `nep141:sol-df27d7abcc1c656d4ac3b1399bbfbba1994e6d8c.omft.near`, when `createPoaBridgeRoute()` is passed explicitly, can an unprivileged caller make the SDK route the withdrawal through a bridge other than Omni or to a chain other than `sol`, because `PoaBridge.supports` returns false for migrated tokens instead of throwing, so the loop continues to HotBridge/OmniBridge/DirectBridge, sending tokens to a `receiver_id` that does not hold them?

## Target
- File/function: packages/intents-sdk/src/constants/poa-tokens-migrated-to-omni-bridge.ts; poa-bridge.ts `supports`; omni-bridge.ts `supports`, `makeAssetInfo`, `isPoaTokenMigratedToOmniBridge`
- Entrypoint: `IntentsSDK.processWithdrawal` / `createWithdrawalIntents` / `parseAssetId`
- Attacker controls: `assetId` = `nep141:sol-df27d7abcc1c656d4ac3b1399bbfbba1994e6d8c.omft.near`, `routeConfig`
- Exploit idea: `PoaBridge.supports` returns false for migrated tokens instead of throwing, so the loop continues to HotBridge/OmniBridge/DirectBridge
- Invariant to test: Every withdrawal of `sol-df27d7abcc1c656d4ac3b1399bbfbba1994e6d8c.omft.near` must produce an `ft_withdraw` to `omni.bridge.near` with `recipient` on its migrated origin chain, regardless of routeConfig; anything else must throw.
- Expected Immunefi impact: Critical - funds delivered to a wrong address/chain/contract with no recovery (HackenProof: cross-chain address validation / withdrawal processing; Immunefi class: direct theft or permanent loss of user funds)
- Fast validation: vitest: iterate all bridges' `supports()` for this id under each routeConfig and assert only OmniBridge accepts with the expected ChainKind.
