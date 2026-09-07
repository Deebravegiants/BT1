# Q0844: Route confusion nep141:base-0x833589fcd6edb6e08f4c7c32d4 + `createVirtualChainRoute(auroraEng (estimateWithdrawalFee)

## Question
An integrator forwards a user's `assetId` = `nep141:base-0x833589fcd6edb6e08f4c7c32d4f71b54bda02913.omft.near` (PoA factory ERC-20 (USDC on Base), prefix `base-`) with `createVirtualChainRoute(auroraEngineContractId, proxyTokenContractId)` into `IntentsSDK.estimateWithdrawalFee` with `amount: 0n, feeInclusive: false`. Given that `AuroraEngineBridge` sends `ft_withdraw` to the caller-named contract with an EVM-address msg, is there an input (destination, memo, or chain) for which the bridge that `supports()` selects differs from the bridge that later `createWithdrawalIdentifiers` selects for status, or from the custodian of the token, so the signed intent moves funds to a contract that never releases them?

## Target
- File/function: packages/intents-sdk/src/sdk.ts `IntentsSDK.bridges` ordering, `createWithdrawalIntents`; bridge `supports()` / `parseAssetId()` in each bridges/*/ file
- Entrypoint: `IntentsSDK.estimateWithdrawalFee` with `amount: 0n, feeInclusive: false` (sets `skipMinAmountValidation` and still runs `validateWithdrawal`)
- Attacker controls: `assetId`, `routeConfig` (`createVirtualChainRoute(auroraEngineContractId, proxyTokenContractId)`), `destinationAddress`
- Exploit idea: `AuroraEngineBridge` sends `ft_withdraw` to the caller-named contract with an EVM-address msg. Token specifics: PoA factory ERC-20 (USDC on Base), prefix `base-`.
- Invariant to test: The bridge contract and chain named by the produced intent must equal the custodian of `nep141:base-0x833589fcd6edb6e08f4c7c32d4f71b54bda02913.omft.near` and the chain the caller named; a mismatch must throw, never fall through to the next bridge.
- Expected Immunefi impact: Critical - funds delivered to a wrong address/chain/contract with no recovery (HackenProof: cross-chain address validation / withdrawal processing; Immunefi class: direct theft or permanent loss of user funds)
- Fast validation: vitest: construct IntentsSDK with mocked RPC/HTTP, call `IntentsSDK.estimateWithdrawalFee` with `amount: 0n, feeInclusive: false` with `nep141:base-0x833589fcd6edb6e08f4c7c32d4f71b54bda02913.omft.near` and `createVirtualChainRoute(auroraEngineContractId, proxyTokenContractId)`, assert `bridge.route` and the intent's `receiver_id`/`recipient`/chain.
