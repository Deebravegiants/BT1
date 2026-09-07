# Q5228: Route confusion nep141:lsd-usdt.rhealab.near + `createOmniBridgeRoute()` with no  (estimateWithdrawalFee)

## Question
Trace `IntentsSDK.estimateWithdrawalFee` with `amount: 0n, feeInclusive: false` for `nep141:lsd-usdt.rhealab.near` (in `FEE_SUBSIDIZED_TOKENS`; fee forced to 0 after the API returned one) under `createOmniBridgeRoute()` with no chain: `OmniBridge.supports` requires a valid omni token or migrated PoA token, throws otherwise. Can an unprivileged caller obtain a signed `IntentPrimitive[]` whose `receiver_id`/`recipient`/chain does not match the token's real bridge, without any bridge throwing, and does the SDK then report `completed`?

## Target
- File/function: packages/intents-sdk/src/sdk.ts `IntentsSDK.bridges` ordering, `createWithdrawalIntents`; bridge `supports()` / `parseAssetId()` in each bridges/*/ file
- Entrypoint: `IntentsSDK.estimateWithdrawalFee` with `amount: 0n, feeInclusive: false` (sets `skipMinAmountValidation` and still runs `validateWithdrawal`)
- Attacker controls: `assetId`, `routeConfig` (`createOmniBridgeRoute()` with no chain), `destinationAddress`
- Exploit idea: `OmniBridge.supports` requires a valid omni token or migrated PoA token, throws otherwise. Token specifics: in `FEE_SUBSIDIZED_TOKENS`; fee forced to 0 after the API returned one.
- Invariant to test: The bridge contract and chain named by the produced intent must equal the custodian of `nep141:lsd-usdt.rhealab.near` and the chain the caller named; a mismatch must throw, never fall through to the next bridge.
- Expected Immunefi impact: Critical - funds delivered to a wrong address/chain/contract with no recovery (HackenProof: cross-chain address validation / withdrawal processing; Immunefi class: direct theft or permanent loss of user funds)
- Fast validation: vitest: construct IntentsSDK with mocked RPC/HTTP, call `IntentsSDK.estimateWithdrawalFee` with `amount: 0n, feeInclusive: false` with `nep141:lsd-usdt.rhealab.near` and `createOmniBridgeRoute()` with no chain, assert `bridge.route` and the intent's `receiver_id`/`recipient`/chain.
