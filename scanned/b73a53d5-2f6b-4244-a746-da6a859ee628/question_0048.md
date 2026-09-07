# Q0048: Route confusion nep141:wrap.near + `createOmniBridgeRoute(chain)` nam (createWithdrawalIntents)

## Question
With `assetId` = `nep141:wrap.near` (`NEAR_NATIVE_ASSET_ID`; Direct route emits `native_withdraw` unless `msg` is set; Omni route treats it as the fee asset) and `createOmniBridgeRoute(chain)` naming a different chain than the token's origin, can an unprivileged caller of `IntentsSDK.createWithdrawalIntents` make bridge selection pick a bridge or destination chain that does not custody this token (because `OmniBridge.supports` accepts any nep141 once `routeConfig.chain` is set and only checks `getBridgedToken` != null), so the emitted `ft_withdraw`/`mt_withdraw`/`transfer` carries `receiver_id`/`recipient` for the wrong contract or chain and the funds are burned or stranded?

## Target
- File/function: packages/intents-sdk/src/sdk.ts `IntentsSDK.bridges` ordering, `createWithdrawalIntents`; bridge `supports()` / `parseAssetId()` in each bridges/*/ file
- Entrypoint: `IntentsSDK.createWithdrawalIntents` (returns raw `IntentPrimitive[]` for the integrator to sign with any signer)
- Attacker controls: `assetId`, `routeConfig` (`createOmniBridgeRoute(chain)` naming a different chain than the token's origin), `destinationAddress`
- Exploit idea: `OmniBridge.supports` accepts any nep141 once `routeConfig.chain` is set and only checks `getBridgedToken` != null. Token specifics: `NEAR_NATIVE_ASSET_ID`; Direct route emits `native_withdraw` unless `msg` is set; Omni route treats it as the fee asset.
- Invariant to test: The bridge contract and chain named by the produced intent must equal the custodian of `nep141:wrap.near` and the chain the caller named; a mismatch must throw, never fall through to the next bridge.
- Expected Immunefi impact: Critical - funds delivered to a wrong address/chain/contract with no recovery (HackenProof: cross-chain address validation / withdrawal processing; Immunefi class: direct theft or permanent loss of user funds)
- Fast validation: vitest: construct IntentsSDK with mocked RPC/HTTP, call `IntentsSDK.createWithdrawalIntents` with `nep141:wrap.near` and `createOmniBridgeRoute(chain)` naming a different chain than the token's origin, assert `bridge.route` and the intent's `receiver_id`/`recipient`/chain.
