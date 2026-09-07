# Q4829: Route confusion nep141:nbtc.bridge.near + `createOmniBridgeRoute()` with no  (signAndSendWithdrawalIntent)

## Question
With `assetId` = `nep141:nbtc.bridge.near` (Omni native BTC (UTXO chain: `utxoMaxGasFee` + `utxoProtocolFee` added to amount, `MaxGasFee` msg)) and `createOmniBridgeRoute()` with no chain, can an unprivileged caller of `IntentsSDK.signAndSendWithdrawalIntent` with a caller-supplied `feeEstimation` make bridge selection pick a bridge or destination chain that does not custody this token (because `OmniBridge.supports` requires a valid omni token or migrated PoA token, throws otherwise), so the emitted `ft_withdraw`/`mt_withdraw`/`transfer` carries `receiver_id`/`recipient` for the wrong contract or chain and the funds are burned or stranded?

## Target
- File/function: packages/intents-sdk/src/sdk.ts `IntentsSDK.bridges` ordering, `createWithdrawalIntents`; bridge `supports()` / `parseAssetId()` in each bridges/*/ file
- Entrypoint: `IntentsSDK.signAndSendWithdrawalIntent` with a caller-supplied `feeEstimation` (skips `_estimateWithdrawalFee`'s `FeeExceedsAmountError` and re-validates only inside `createWithdrawalIntents`)
- Attacker controls: `assetId`, `routeConfig` (`createOmniBridgeRoute()` with no chain), `destinationAddress`
- Exploit idea: `OmniBridge.supports` requires a valid omni token or migrated PoA token, throws otherwise. Token specifics: Omni native BTC (UTXO chain: `utxoMaxGasFee` + `utxoProtocolFee` added to amount, `MaxGasFee` msg).
- Invariant to test: The bridge contract and chain named by the produced intent must equal the custodian of `nep141:nbtc.bridge.near` and the chain the caller named; a mismatch must throw, never fall through to the next bridge.
- Expected Immunefi impact: Critical - funds delivered to a wrong address/chain/contract with no recovery (HackenProof: cross-chain address validation / withdrawal processing; Immunefi class: direct theft or permanent loss of user funds)
- Fast validation: vitest: construct IntentsSDK with mocked RPC/HTTP, call `IntentsSDK.signAndSendWithdrawalIntent` with a caller-supplied `feeEstimation` with `nep141:nbtc.bridge.near` and `createOmniBridgeRoute()` with no chain, assert `bridge.route` and the intent's `receiver_id`/`recipient`/chain.
