# Q2093: TON uninitialised wallet, bounceable form on HotBridge feeInclusive: false

## Question
For a TON withdrawal over HotBridge with `feeInclusive: false`, `validateAddress` accepts a uninitialised wallet, bounceable form such as `EQCxE6mUtQJKFnGfaROTKOt1lZbDiiX1kCixRv7Nw2Id_sDs` (format check only, as the docstring admits). Does `hotSdk.buildGaslessWithdrawIntent` -> `mt_withdraw` on `v2_1.omni.hot.tg` with `receiver` hand this address type to the HOT Omni bridge relayer which cannot or will not pay that script/account type, so the tokens leave the user's intents balance, the bridge cannot deliver, and nothing in `describeWithdrawal` surfaces the failure?

## Target
- File/function: packages/intents-sdk/src/lib/validateAddress.ts `validateTonAddress`; packages/intents-sdk/src/bridges/hot-bridge/hot-bridge.ts `validateWithdrawal`, `createWithdrawalIntents`, `describeWithdrawal`
- Entrypoint: `IntentsSDK.processWithdrawal` / `createWithdrawalIntents`
- Attacker controls: `destinationAddress` = `EQCxE6mUtQJKFnGfaROTKOt1lZbDiiX1kCixRv7Nw2Id_sDs` (uninitialised wallet, bounceable form), `assetId` for TON, `feeInclusive`
- Exploit idea: Validation is format-only; bridge capability for uninitialised wallet, bounceable form on TON is not encoded anywhere in the SDK. The intent is irrevocable once settled on intents.near.
- Invariant to test: validateAddress(s, TON) == true implies the hot bridge can deliver to s; otherwise the SDK must reject before signing.
- Expected Immunefi impact: High - withdrawal stuck or refunded to the wrong account until manual intervention (HackenProof: withdrawal processing; Immunefi class: temporary freezing of funds)
- Fast validation: vitest: assert `validateAddress('EQCxE6mUtQJKFnGfaROTKOt1lZbDiiX1kCixRv7Nw2Id_sDs', Chains.TON)`; cross-check the hot bridge's supported address types (live docs/API) and, if unsupported, this is a pre-sign validation gap.
