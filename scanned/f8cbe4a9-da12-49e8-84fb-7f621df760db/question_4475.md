# Q4475: Route confusion nep141:aptos.omft.near + `createNearWithdrawalRoute(msg)` w (estimateWithdrawalFee)

## Question
Trace `IntentsSDK.estimateWithdrawalFee` with `amount: 0n, feeInclusive: false` for `nep141:aptos.omft.near` (MIGRATED to Omni (ChainKind.Aptos)) under `createNearWithdrawalRoute(msg)` with an attacker-chosen `msg`: `DirectBridge` forwards `msg` into `ft_withdraw`, turning it into `ft_transfer_call` on `receiver_id`. Can an unprivileged caller obtain a signed `IntentPrimitive[]` whose `receiver_id`/`recipient`/chain does not match the token's real bridge, without any bridge throwing, and does the SDK then report `completed`?

## Target
- File/function: packages/intents-sdk/src/sdk.ts `IntentsSDK.bridges` ordering, `createWithdrawalIntents`; bridge `supports()` / `parseAssetId()` in each bridges/*/ file
- Entrypoint: `IntentsSDK.estimateWithdrawalFee` with `amount: 0n, feeInclusive: false` (sets `skipMinAmountValidation` and still runs `validateWithdrawal`)
- Attacker controls: `assetId`, `routeConfig` (`createNearWithdrawalRoute(msg)` with an attacker-chosen `msg`), `destinationAddress`
- Exploit idea: `DirectBridge` forwards `msg` into `ft_withdraw`, turning it into `ft_transfer_call` on `receiver_id`. Token specifics: MIGRATED to Omni (ChainKind.Aptos).
- Invariant to test: The bridge contract and chain named by the produced intent must equal the custodian of `nep141:aptos.omft.near` and the chain the caller named; a mismatch must throw, never fall through to the next bridge.
- Expected Immunefi impact: Critical - funds delivered to a wrong address/chain/contract with no recovery (HackenProof: cross-chain address validation / withdrawal processing; Immunefi class: direct theft or permanent loss of user funds)
- Fast validation: vitest: construct IntentsSDK with mocked RPC/HTTP, call `IntentsSDK.estimateWithdrawalFee` with `amount: 0n, feeInclusive: false` with `nep141:aptos.omft.near` and `createNearWithdrawalRoute(msg)` with an attacker-chosen `msg`, assert `bridge.route` and the intent's `receiver_id`/`recipient`/chain.
