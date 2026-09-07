# Q4304: Route confusion nep141:sol-5ce3bf3a31af18be40ba30f721101 + `createVirtualChainRoute(auroraEng (signAndSendWithdrawalIntent)

## Question
Trace `IntentsSDK.signAndSendWithdrawalIntent` with a caller-supplied `feeEstimation` for `nep141:sol-5ce3bf3a31af18be40ba30f721101b4341690186.omft.near` (MIGRATED USDC (Solana) to Omni) under `createVirtualChainRoute(auroraEngineContractId, proxyTokenContractId)`: `AuroraEngineBridge` sends `ft_withdraw` to the caller-named contract with an EVM-address msg. Can an unprivileged caller obtain a signed `IntentPrimitive[]` whose `receiver_id`/`recipient`/chain does not match the token's real bridge, without any bridge throwing, and does the SDK then report `completed`?

## Target
- File/function: packages/intents-sdk/src/sdk.ts `IntentsSDK.bridges` ordering, `createWithdrawalIntents`; bridge `supports()` / `parseAssetId()` in each bridges/*/ file
- Entrypoint: `IntentsSDK.signAndSendWithdrawalIntent` with a caller-supplied `feeEstimation` (skips `_estimateWithdrawalFee`'s `FeeExceedsAmountError` and re-validates only inside `createWithdrawalIntents`)
- Attacker controls: `assetId`, `routeConfig` (`createVirtualChainRoute(auroraEngineContractId, proxyTokenContractId)`), `destinationAddress`
- Exploit idea: `AuroraEngineBridge` sends `ft_withdraw` to the caller-named contract with an EVM-address msg. Token specifics: MIGRATED USDC (Solana) to Omni.
- Invariant to test: The bridge contract and chain named by the produced intent must equal the custodian of `nep141:sol-5ce3bf3a31af18be40ba30f721101b4341690186.omft.near` and the chain the caller named; a mismatch must throw, never fall through to the next bridge.
- Expected Immunefi impact: Critical - funds delivered to a wrong address/chain/contract with no recovery (HackenProof: cross-chain address validation / withdrawal processing; Immunefi class: direct theft or permanent loss of user funds)
- Fast validation: vitest: construct IntentsSDK with mocked RPC/HTTP, call `IntentsSDK.signAndSendWithdrawalIntent` with a caller-supplied `feeEstimation` with `nep141:sol-5ce3bf3a31af18be40ba30f721101b4341690186.omft.near` and `createVirtualChainRoute(auroraEngineContractId, proxyTokenContractId)`, assert `bridge.route` and the intent's `receiver_id`/`recipient`/chain.
