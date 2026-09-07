# Q5515: Route confusion nep245:v2_1.omni.hot.tg:137_2791bca1f2de + `createHotBridgeRoute(chain)` (processWithdrawal)

## Question
With `assetId` = `nep245:v2_1.omni.hot.tg:137_2791bca1f2de4661ed88a30c99a7a9449aa84174` (HOT ERC-20 on Polygon (USDC.e)) and `createHotBridgeRoute(chain)`, can an unprivileged caller of `IntentsSDK.processWithdrawal` make bridge selection pick a bridge or destination chain that does not custody this token (because `HotBridge.supports` ignores `routeConfig.chain` entirely and derives the chain from the nep245 token id), so the emitted `ft_withdraw`/`mt_withdraw`/`transfer` carries `receiver_id`/`recipient` for the wrong contract or chain and the funds are burned or stranded?

## Target
- File/function: packages/intents-sdk/src/sdk.ts `IntentsSDK.bridges` ordering, `createWithdrawalIntents`; bridge `supports()` / `parseAssetId()` in each bridges/*/ file
- Entrypoint: `IntentsSDK.processWithdrawal` (end-to-end: estimate -> validate -> sign -> publish -> wait)
- Attacker controls: `assetId`, `routeConfig` (`createHotBridgeRoute(chain)`), `destinationAddress`
- Exploit idea: `HotBridge.supports` ignores `routeConfig.chain` entirely and derives the chain from the nep245 token id. Token specifics: HOT ERC-20 on Polygon (USDC.e).
- Invariant to test: The bridge contract and chain named by the produced intent must equal the custodian of `nep245:v2_1.omni.hot.tg:137_2791bca1f2de4661ed88a30c99a7a9449aa84174` and the chain the caller named; a mismatch must throw, never fall through to the next bridge.
- Expected Immunefi impact: Critical - funds delivered to a wrong address/chain/contract with no recovery (HackenProof: cross-chain address validation / withdrawal processing; Immunefi class: direct theft or permanent loss of user funds)
- Fast validation: vitest: construct IntentsSDK with mocked RPC/HTTP, call `IntentsSDK.processWithdrawal` with `nep245:v2_1.omni.hot.tg:137_2791bca1f2de4661ed88a30c99a7a9449aa84174` and `createHotBridgeRoute(chain)`, assert `bridge.route` and the intent's `receiver_id`/`recipient`/chain.
