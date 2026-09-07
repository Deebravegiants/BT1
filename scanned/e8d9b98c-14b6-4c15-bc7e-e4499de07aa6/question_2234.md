# Q2234: TON masterchain `-1:` raw on HotBridge feeInclusive: false

## Question
For a TON withdrawal over HotBridge with `feeInclusive: false`, `validateAddress` accepts a masterchain `-1:` raw such as `-1:3333333333333333333333333333333333333333333333333333333333333333` (format check only, as the docstring admits). Does `hotSdk.buildGaslessWithdrawIntent` -> `mt_withdraw` on `v2_1.omni.hot.tg` with `receiver` hand this address type to the HOT Omni bridge relayer which cannot or will not pay that script/account type, so the tokens leave the user's intents balance, the bridge cannot deliver, and nothing in `describeWithdrawal` surfaces the failure?

## Target
- File/function: packages/intents-sdk/src/lib/validateAddress.ts `validateTonAddress`; packages/intents-sdk/src/bridges/hot-bridge/hot-bridge.ts `validateWithdrawal`, `createWithdrawalIntents`, `describeWithdrawal`
- Entrypoint: `IntentsSDK.processWithdrawal` / `createWithdrawalIntents`
- Attacker controls: `destinationAddress` = `-1:3333333333333333333333333333333333333333333333333333333333333333` (masterchain `-1:` raw), `assetId` for TON, `feeInclusive`
- Exploit idea: Validation is format-only; bridge capability for masterchain `-1:` raw on TON is not encoded anywhere in the SDK. The intent is irrevocable once settled on intents.near.
- Invariant to test: validateAddress(s, TON) == true implies the hot bridge can deliver to s; otherwise the SDK must reject before signing.
- Expected Immunefi impact: High - withdrawal stuck or refunded to the wrong account until manual intervention (HackenProof: withdrawal processing; Immunefi class: temporary freezing of funds)
- Fast validation: vitest: assert `validateAddress('-1:3333333333333333333333333333333333333333333333333333333333333333', Chains.TON)`; cross-check the hot bridge's supported address types (live docs/API) and, if unsupported, this is a pre-sign validation gap.
