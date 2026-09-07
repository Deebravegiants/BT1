# Q5815: Route confusion nep245:v2_1.omni.hot.tg:9745_11111111111 + `createHotBridgeRoute(chain)` (createWithdrawalIntents)

## Question
With `assetId` = `nep245:v2_1.omni.hot.tg:9745_11111111111111111111` (HOT native XPL; `gasPrice *= 100n` for non-native tokens on Plasma) and `createHotBridgeRoute(chain)`, can an unprivileged caller of `IntentsSDK.createWithdrawalIntents` make bridge selection pick a bridge or destination chain that does not custody this token (because `HotBridge.supports` ignores `routeConfig.chain` entirely and derives the chain from the nep245 token id), so the emitted `ft_withdraw`/`mt_withdraw`/`transfer` carries `receiver_id`/`recipient` for the wrong contract or chain and the funds are burned or stranded?

## Target
- File/function: packages/intents-sdk/src/sdk.ts `IntentsSDK.bridges` ordering, `createWithdrawalIntents`; bridge `supports()` / `parseAssetId()` in each bridges/*/ file
- Entrypoint: `IntentsSDK.createWithdrawalIntents` (returns raw `IntentPrimitive[]` for the integrator to sign with any signer)
- Attacker controls: `assetId`, `routeConfig` (`createHotBridgeRoute(chain)`), `destinationAddress`
- Exploit idea: `HotBridge.supports` ignores `routeConfig.chain` entirely and derives the chain from the nep245 token id. Token specifics: HOT native XPL; `gasPrice *= 100n` for non-native tokens on Plasma.
- Invariant to test: The bridge contract and chain named by the produced intent must equal the custodian of `nep245:v2_1.omni.hot.tg:9745_11111111111111111111` and the chain the caller named; a mismatch must throw, never fall through to the next bridge.
- Expected Immunefi impact: Critical - funds delivered to a wrong address/chain/contract with no recovery (HackenProof: cross-chain address validation / withdrawal processing; Immunefi class: direct theft or permanent loss of user funds)
- Fast validation: vitest: construct IntentsSDK with mocked RPC/HTTP, call `IntentsSDK.createWithdrawalIntents` with `nep245:v2_1.omni.hot.tg:9745_11111111111111111111` and `createHotBridgeRoute(chain)`, assert `bridge.route` and the intent's `receiver_id`/`recipient`/chain.
