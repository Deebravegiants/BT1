# Q0643: Route confusion nep141:eth.omft.near + `createVirtualChainRoute(auroraEng (signAndSendWithdrawalIntent)

## Question
An integrator forwards a user's `assetId` = `nep141:eth.omft.near` (PoA factory native ETH) with `createVirtualChainRoute(auroraEngineContractId, proxyTokenContractId)` into `IntentsSDK.signAndSendWithdrawalIntent` with a caller-supplied `feeEstimation`. Given that `AuroraEngineBridge` sends `ft_withdraw` to the caller-named contract with an EVM-address msg, is there an input (destination, memo, or chain) for which the bridge that `supports()` selects differs from the bridge that later `createWithdrawalIdentifiers` selects for status, or from the custodian of the token, so the signed intent moves funds to a contract that never releases them?

## Target
- File/function: packages/intents-sdk/src/sdk.ts `IntentsSDK.bridges` ordering, `createWithdrawalIntents`; bridge `supports()` / `parseAssetId()` in each bridges/*/ file
- Entrypoint: `IntentsSDK.signAndSendWithdrawalIntent` with a caller-supplied `feeEstimation` (skips `_estimateWithdrawalFee`'s `FeeExceedsAmountError` and re-validates only inside `createWithdrawalIntents`)
- Attacker controls: `assetId`, `routeConfig` (`createVirtualChainRoute(auroraEngineContractId, proxyTokenContractId)`), `destinationAddress`
- Exploit idea: `AuroraEngineBridge` sends `ft_withdraw` to the caller-named contract with an EVM-address msg. Token specifics: PoA factory native ETH.
- Invariant to test: The bridge contract and chain named by the produced intent must equal the custodian of `nep141:eth.omft.near` and the chain the caller named; a mismatch must throw, never fall through to the next bridge.
- Expected Immunefi impact: Critical - funds delivered to a wrong address/chain/contract with no recovery (HackenProof: cross-chain address validation / withdrawal processing; Immunefi class: direct theft or permanent loss of user funds)
- Fast validation: vitest: construct IntentsSDK with mocked RPC/HTTP, call `IntentsSDK.signAndSendWithdrawalIntent` with a caller-supplied `feeEstimation` with `nep141:eth.omft.near` and `createVirtualChainRoute(auroraEngineContractId, proxyTokenContractId)`, assert `bridge.route` and the intent's `receiver_id`/`recipient`/chain.
