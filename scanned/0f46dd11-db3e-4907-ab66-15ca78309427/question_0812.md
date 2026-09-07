# Q0812: Route confusion nep141:base-0x833589fcd6edb6e08f4c7c32d4 + `createInternalTransferRoute()` (estimateWithdrawalFee)

## Question
With `assetId` = `nep141:base-0x833589fcd6edb6e08f4c7c32d4f71b54bda02913.omft.near` (PoA factory ERC-20 (USDC on Base), prefix `base-`) and `createInternalTransferRoute()`, can an unprivileged caller of `IntentsSDK.estimateWithdrawalFee` with `amount: 0n, feeInclusive: false` make bridge selection pick a bridge or destination chain that does not custody this token (because `IntentsBridge` emits `transfer` to any `receiver_id` with no asset checks), so the emitted `ft_withdraw`/`mt_withdraw`/`transfer` carries `receiver_id`/`recipient` for the wrong contract or chain and the funds are burned or stranded?

## Target
- File/function: packages/intents-sdk/src/sdk.ts `IntentsSDK.bridges` ordering, `createWithdrawalIntents`; bridge `supports()` / `parseAssetId()` in each bridges/*/ file
- Entrypoint: `IntentsSDK.estimateWithdrawalFee` with `amount: 0n, feeInclusive: false` (sets `skipMinAmountValidation` and still runs `validateWithdrawal`)
- Attacker controls: `assetId`, `routeConfig` (`createInternalTransferRoute()`), `destinationAddress`
- Exploit idea: `IntentsBridge` emits `transfer` to any `receiver_id` with no asset checks. Token specifics: PoA factory ERC-20 (USDC on Base), prefix `base-`.
- Invariant to test: The bridge contract and chain named by the produced intent must equal the custodian of `nep141:base-0x833589fcd6edb6e08f4c7c32d4f71b54bda02913.omft.near` and the chain the caller named; a mismatch must throw, never fall through to the next bridge.
- Expected Immunefi impact: Critical - funds delivered to a wrong address/chain/contract with no recovery (HackenProof: cross-chain address validation / withdrawal processing; Immunefi class: direct theft or permanent loss of user funds)
- Fast validation: vitest: construct IntentsSDK with mocked RPC/HTTP, call `IntentsSDK.estimateWithdrawalFee` with `amount: 0n, feeInclusive: false` with `nep141:base-0x833589fcd6edb6e08f4c7c32d4f71b54bda02913.omft.near` and `createInternalTransferRoute()`, assert `bridge.route` and the intent's `receiver_id`/`recipient`/chain.
