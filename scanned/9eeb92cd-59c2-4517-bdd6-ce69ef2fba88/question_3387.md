# Q3387: HOT tokenId parse 43114_ (Avalanche)

## Question
Can an unprivileged caller pass `assetId` = `nep245:v2_1.omni.hot.tg:43114_` so that `HotBridge.parseAssetId` splits `utils.fromOmni(tokenId)` on ':' into chainId `43114` (Avalanche) and an address that is neither `native` nor a real token, then `createWithdrawalIntents` calls `buildGaslessWithdrawIntent` with `token` = that address and the `mt_withdraw` burns a HOT token id that has no on-chain backing on Avalanche?

## Target
- File/function: packages/intents-sdk/src/bridges/hot-bridge/hot-bridge.ts `parseAssetId`, `createWithdrawalIntents`; hot-bridge-utils.ts `hotNetworkIdToCAIP2`, `toHotNetworkId`
- Entrypoint: `IntentsSDK.processWithdrawal` / `createWithdrawalIntents`
- Attacker controls: `assetId` nep245 token id `43114_`
- Exploit idea: The token id is split on ':' after `fromOmni`; only `chainId == null || address == null` is rejected. `native` is detected by string equality; anything else becomes `assetInfo.address` and later `token` for HOT SDK.
- Invariant to test: `parseAssetId` must only accept token ids HOT actually issued for that chain; `mt_withdraw` must reference a token id the user holds and HOT can redeem on the named chain.
- Expected Immunefi impact: Critical - funds delivered to a wrong address/chain/contract with no recovery (HackenProof: cross-chain address validation / withdrawal processing; Immunefi class: direct theft or permanent loss of user funds)
- Fast validation: vitest: `new HotBridge(...).parseAssetId(id)` and inspect `address`/`native`; mock `buildGaslessWithdrawIntent` and assert `token`.
