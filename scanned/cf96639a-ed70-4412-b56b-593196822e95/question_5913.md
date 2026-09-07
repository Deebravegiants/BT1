# Q5913: Migrated sol-df27d7abcc1c656d4ac3b1399b: no routeConfig and `getBridgedToken` ret

## Question
For migrated PoA token `nep141:sol-df27d7abcc1c656d4ac3b1399bbfbba1994e6d8c.omft.near`, when no routeConfig and `getBridgedToken` returns null for the migrated token, can an unprivileged caller make the SDK route the withdrawal through a bridge other than Omni or to a chain other than `sol`, because `OmniBridge.supports` throws `TokenNotFoundInDestinationChainError` and DirectBridge is never reached; but `parseAssetId` on IntentsSDK still returns the Omni info, sending tokens to a `receiver_id` that does not hold them?

## Target
- File/function: packages/intents-sdk/src/constants/poa-tokens-migrated-to-omni-bridge.ts; poa-bridge.ts `supports`; omni-bridge.ts `supports`, `makeAssetInfo`, `isPoaTokenMigratedToOmniBridge`
- Entrypoint: `IntentsSDK.processWithdrawal` / `createWithdrawalIntents` / `parseAssetId`
- Attacker controls: `assetId` = `nep141:sol-df27d7abcc1c656d4ac3b1399bbfbba1994e6d8c.omft.near`, `routeConfig`
- Exploit idea: `OmniBridge.supports` throws `TokenNotFoundInDestinationChainError` and DirectBridge is never reached; but `parseAssetId` on IntentsSDK still returns the Omni info
- Invariant to test: Every withdrawal of `sol-df27d7abcc1c656d4ac3b1399bbfbba1994e6d8c.omft.near` must produce an `ft_withdraw` to `omni.bridge.near` with `recipient` on its migrated origin chain, regardless of routeConfig; anything else must throw.
- Expected Immunefi impact: Critical - funds delivered to a wrong address/chain/contract with no recovery (HackenProof: cross-chain address validation / withdrawal processing; Immunefi class: direct theft or permanent loss of user funds)
- Fast validation: vitest: iterate all bridges' `supports()` for this id under each routeConfig and assert only OmniBridge accepts with the expected ChainKind.
