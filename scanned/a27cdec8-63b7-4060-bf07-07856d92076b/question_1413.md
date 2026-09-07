# Q1413: Route confusion nep141:doge.omft.near + `createPoaBridgeRoute()` (processWithdrawal)

## Question
With `assetId` = `nep141:doge.omft.near` (PoA native Doge) and `createPoaBridgeRoute()`, can an unprivileged caller of `IntentsSDK.processWithdrawal` make bridge selection pick a bridge or destination chain that does not custody this token (because `PoaBridge.supports` throws `UnsupportedAssetIdError` if the asset is not PoA, but migrated tokens return false silently), so the emitted `ft_withdraw`/`mt_withdraw`/`transfer` carries `receiver_id`/`recipient` for the wrong contract or chain and the funds are burned or stranded?

## Target
- File/function: packages/intents-sdk/src/sdk.ts `IntentsSDK.bridges` ordering, `createWithdrawalIntents`; bridge `supports()` / `parseAssetId()` in each bridges/*/ file
- Entrypoint: `IntentsSDK.processWithdrawal` (end-to-end: estimate -> validate -> sign -> publish -> wait)
- Attacker controls: `assetId`, `routeConfig` (`createPoaBridgeRoute()`), `destinationAddress`
- Exploit idea: `PoaBridge.supports` throws `UnsupportedAssetIdError` if the asset is not PoA, but migrated tokens return false silently. Token specifics: PoA native Doge.
- Invariant to test: The bridge contract and chain named by the produced intent must equal the custodian of `nep141:doge.omft.near` and the chain the caller named; a mismatch must throw, never fall through to the next bridge.
- Expected Immunefi impact: Critical - funds delivered to a wrong address/chain/contract with no recovery (HackenProof: cross-chain address validation / withdrawal processing; Immunefi class: direct theft or permanent loss of user funds)
- Fast validation: vitest: construct IntentsSDK with mocked RPC/HTTP, call `IntentsSDK.processWithdrawal` with `nep141:doge.omft.near` and `createPoaBridgeRoute()`, assert `bridge.route` and the intent's `receiver_id`/`recipient`/chain.
