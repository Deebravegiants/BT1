# Q1219: Route confusion nep141:xrp.omft.near + `createVirtualChainRoute(auroraEng (estimateWithdrawalFee)

## Question
Trace `IntentsSDK.estimateWithdrawalFee` with `amount: 0n, feeInclusive: false` for `nep141:xrp.omft.near` (the only asset where `XrplAccountNotFundedError` is tolerated) under `createVirtualChainRoute(auroraEngineContractId, proxyTokenContractId)`: `AuroraEngineBridge` sends `ft_withdraw` to the caller-named contract with an EVM-address msg. Can an unprivileged caller obtain a signed `IntentPrimitive[]` whose `receiver_id`/`recipient`/chain does not match the token's real bridge, without any bridge throwing, and does the SDK then report `completed`?

## Target
- File/function: packages/intents-sdk/src/sdk.ts `IntentsSDK.bridges` ordering, `createWithdrawalIntents`; bridge `supports()` / `parseAssetId()` in each bridges/*/ file
- Entrypoint: `IntentsSDK.estimateWithdrawalFee` with `amount: 0n, feeInclusive: false` (sets `skipMinAmountValidation` and still runs `validateWithdrawal`)
- Attacker controls: `assetId`, `routeConfig` (`createVirtualChainRoute(auroraEngineContractId, proxyTokenContractId)`), `destinationAddress`
- Exploit idea: `AuroraEngineBridge` sends `ft_withdraw` to the caller-named contract with an EVM-address msg. Token specifics: the only asset where `XrplAccountNotFundedError` is tolerated.
- Invariant to test: The bridge contract and chain named by the produced intent must equal the custodian of `nep141:xrp.omft.near` and the chain the caller named; a mismatch must throw, never fall through to the next bridge.
- Expected Immunefi impact: Critical - funds delivered to a wrong address/chain/contract with no recovery (HackenProof: cross-chain address validation / withdrawal processing; Immunefi class: direct theft or permanent loss of user funds)
- Fast validation: vitest: construct IntentsSDK with mocked RPC/HTTP, call `IntentsSDK.estimateWithdrawalFee` with `amount: 0n, feeInclusive: false` with `nep141:xrp.omft.near` and `createVirtualChainRoute(auroraEngineContractId, proxyTokenContractId)`, assert `bridge.route` and the intent's `receiver_id`/`recipient`/chain.
