# Q0695: Migrated sol-c800a4bd850783ccb82c2b2c7e: `createOmniBridgeRoute(otherChain)` name

## Question
For migrated PoA token `nep141:sol-c800a4bd850783ccb82c2b2c7e84175443606352.omft.near`, when `createOmniBridgeRoute(otherChain)` names a chain other than the migrated token's origin, can an unprivileged caller make the SDK route the withdrawal through a bridge other than Omni or to a chain other than `sol`, because `poaContractIdToChainKind` is bypassed because `targetChainSpecified` takes the caller's chain, sending tokens to a `receiver_id` that does not hold them?

## Target
- File/function: packages/intents-sdk/src/constants/poa-tokens-migrated-to-omni-bridge.ts; poa-bridge.ts `supports`; omni-bridge.ts `supports`, `makeAssetInfo`, `isPoaTokenMigratedToOmniBridge`
- Entrypoint: `IntentsSDK.processWithdrawal` / `createWithdrawalIntents` / `parseAssetId`
- Attacker controls: `assetId` = `nep141:sol-c800a4bd850783ccb82c2b2c7e84175443606352.omft.near`, `routeConfig`
- Exploit idea: `poaContractIdToChainKind` is bypassed because `targetChainSpecified` takes the caller's chain
- Invariant to test: Every withdrawal of `sol-c800a4bd850783ccb82c2b2c7e84175443606352.omft.near` must produce an `ft_withdraw` to `omni.bridge.near` with `recipient` on its migrated origin chain, regardless of routeConfig; anything else must throw.
- Expected Immunefi impact: Critical - funds delivered to a wrong address/chain/contract with no recovery (HackenProof: cross-chain address validation / withdrawal processing; Immunefi class: direct theft or permanent loss of user funds)
- Fast validation: vitest: iterate all bridges' `supports()` for this id under each routeConfig and assert only OmniBridge accepts with the expected ChainKind.
