# Q5483: Route confusion nep245:v2_1.omni.hot.tg:137_2791bca1f2de + `createInternalTransferRoute()` (processWithdrawal)

## Question
An integrator forwards a user's `assetId` = `nep245:v2_1.omni.hot.tg:137_2791bca1f2de4661ed88a30c99a7a9449aa84174` (HOT ERC-20 on Polygon (USDC.e)) with `createInternalTransferRoute()` into `IntentsSDK.processWithdrawal`. Given that `IntentsBridge` emits `transfer` to any `receiver_id` with no asset checks, is there an input (destination, memo, or chain) for which the bridge that `supports()` selects differs from the bridge that later `createWithdrawalIdentifiers` selects for status, or from the custodian of the token, so the signed intent moves funds to a contract that never releases them?

## Target
- File/function: packages/intents-sdk/src/sdk.ts `IntentsSDK.bridges` ordering, `createWithdrawalIntents`; bridge `supports()` / `parseAssetId()` in each bridges/*/ file
- Entrypoint: `IntentsSDK.processWithdrawal` (end-to-end: estimate -> validate -> sign -> publish -> wait)
- Attacker controls: `assetId`, `routeConfig` (`createInternalTransferRoute()`), `destinationAddress`
- Exploit idea: `IntentsBridge` emits `transfer` to any `receiver_id` with no asset checks. Token specifics: HOT ERC-20 on Polygon (USDC.e).
- Invariant to test: The bridge contract and chain named by the produced intent must equal the custodian of `nep245:v2_1.omni.hot.tg:137_2791bca1f2de4661ed88a30c99a7a9449aa84174` and the chain the caller named; a mismatch must throw, never fall through to the next bridge.
- Expected Immunefi impact: Critical - funds delivered to a wrong address/chain/contract with no recovery (HackenProof: cross-chain address validation / withdrawal processing; Immunefi class: direct theft or permanent loss of user funds)
- Fast validation: vitest: construct IntentsSDK with mocked RPC/HTTP, call `IntentsSDK.processWithdrawal` with `nep245:v2_1.omni.hot.tg:137_2791bca1f2de4661ed88a30c99a7a9449aa84174` and `createInternalTransferRoute()`, assert `bridge.route` and the intent's `receiver_id`/`recipient`/chain.
