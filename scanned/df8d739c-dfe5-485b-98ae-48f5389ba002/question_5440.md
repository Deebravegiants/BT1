# Q5440: Route confusion nep245:v2_1.omni.hot.tg:56_1111111111111 + `createHotBridgeRoute(chain)` (estimateWithdrawalFee)

## Question
With `assetId` = `nep245:v2_1.omni.hot.tg:56_11111111111111111111` (HOT native BNB, also the fee asset for BNB (`getFeeAssetIdForChain`)) and `createHotBridgeRoute(chain)`, can an unprivileged caller of `IntentsSDK.estimateWithdrawalFee` with `amount: 0n, feeInclusive: false` make bridge selection pick a bridge or destination chain that does not custody this token (because `HotBridge.supports` ignores `routeConfig.chain` entirely and derives the chain from the nep245 token id), so the emitted `ft_withdraw`/`mt_withdraw`/`transfer` carries `receiver_id`/`recipient` for the wrong contract or chain and the funds are burned or stranded?

## Target
- File/function: packages/intents-sdk/src/sdk.ts `IntentsSDK.bridges` ordering, `createWithdrawalIntents`; bridge `supports()` / `parseAssetId()` in each bridges/*/ file
- Entrypoint: `IntentsSDK.estimateWithdrawalFee` with `amount: 0n, feeInclusive: false` (sets `skipMinAmountValidation` and still runs `validateWithdrawal`)
- Attacker controls: `assetId`, `routeConfig` (`createHotBridgeRoute(chain)`), `destinationAddress`
- Exploit idea: `HotBridge.supports` ignores `routeConfig.chain` entirely and derives the chain from the nep245 token id. Token specifics: HOT native BNB, also the fee asset for BNB (`getFeeAssetIdForChain`).
- Invariant to test: The bridge contract and chain named by the produced intent must equal the custodian of `nep245:v2_1.omni.hot.tg:56_11111111111111111111` and the chain the caller named; a mismatch must throw, never fall through to the next bridge.
- Expected Immunefi impact: Critical - funds delivered to a wrong address/chain/contract with no recovery (HackenProof: cross-chain address validation / withdrawal processing; Immunefi class: direct theft or permanent loss of user funds)
- Fast validation: vitest: construct IntentsSDK with mocked RPC/HTTP, call `IntentsSDK.estimateWithdrawalFee` with `amount: 0n, feeInclusive: false` with `nep245:v2_1.omni.hot.tg:56_11111111111111111111` and `createHotBridgeRoute(chain)`, assert `bridge.route` and the intent's `receiver_id`/`recipient`/chain.
