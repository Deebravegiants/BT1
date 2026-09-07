# Q1281: Route confusion nep141:doge.omft.near + no `routeConfig` (default) (estimateWithdrawalFee)

## Question
With `assetId` = `nep141:doge.omft.near` (PoA native Doge) and no `routeConfig` (default), can an unprivileged caller of `IntentsSDK.estimateWithdrawalFee` with `amount: 0n, feeInclusive: false` make bridge selection pick a bridge or destination chain that does not custody this token (because first bridge whose `supports()` is true wins, in order IntentsBridge, AuroraEngineBridge, PoaBridge, HotBridge, OmniBridge, DirectBridge), so the emitted `ft_withdraw`/`mt_withdraw`/`transfer` carries `receiver_id`/`recipient` for the wrong contract or chain and the funds are burned or stranded?

## Target
- File/function: packages/intents-sdk/src/sdk.ts `IntentsSDK.bridges` ordering, `createWithdrawalIntents`; bridge `supports()` / `parseAssetId()` in each bridges/*/ file
- Entrypoint: `IntentsSDK.estimateWithdrawalFee` with `amount: 0n, feeInclusive: false` (sets `skipMinAmountValidation` and still runs `validateWithdrawal`)
- Attacker controls: `assetId`, `routeConfig` (no `routeConfig` (default)), `destinationAddress`
- Exploit idea: first bridge whose `supports()` is true wins, in order IntentsBridge, AuroraEngineBridge, PoaBridge, HotBridge, OmniBridge, DirectBridge. Token specifics: PoA native Doge.
- Invariant to test: The bridge contract and chain named by the produced intent must equal the custodian of `nep141:doge.omft.near` and the chain the caller named; a mismatch must throw, never fall through to the next bridge.
- Expected Immunefi impact: Critical - funds delivered to a wrong address/chain/contract with no recovery (HackenProof: cross-chain address validation / withdrawal processing; Immunefi class: direct theft or permanent loss of user funds)
- Fast validation: vitest: construct IntentsSDK with mocked RPC/HTTP, call `IntentsSDK.estimateWithdrawalFee` with `amount: 0n, feeInclusive: false` with `nep141:doge.omft.near` and no `routeConfig` (default), assert `bridge.route` and the intent's `receiver_id`/`recipient`/chain.
