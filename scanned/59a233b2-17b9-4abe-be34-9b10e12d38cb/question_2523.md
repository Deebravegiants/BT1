# Q2523: Stellar account without trustline on HotBridge feeInclusive: false

## Question
For a Stellar withdrawal over HotBridge with `feeInclusive: false`, `validateAddress` accepts a account without trustline such as `GA5ZSEJYB37JRC5AVCIA5MOP4RHTM335X2KGX3IHOJAPP5RE34K4KZVN` (format check only, as the docstring admits). Does `hotSdk.buildGaslessWithdrawIntent` -> `mt_withdraw` on `v2_1.omni.hot.tg` with `receiver` hand this address type to the HOT Omni bridge relayer which cannot or will not pay that script/account type, so the tokens leave the user's intents balance, the bridge cannot deliver, and nothing in `describeWithdrawal` surfaces the failure?

## Target
- File/function: packages/intents-sdk/src/lib/validateAddress.ts `validateStellarAddress`; packages/intents-sdk/src/bridges/hot-bridge/hot-bridge.ts `validateWithdrawal`, `createWithdrawalIntents`, `describeWithdrawal`
- Entrypoint: `IntentsSDK.processWithdrawal` / `createWithdrawalIntents`
- Attacker controls: `destinationAddress` = `GA5ZSEJYB37JRC5AVCIA5MOP4RHTM335X2KGX3IHOJAPP5RE34K4KZVN` (account without trustline), `assetId` for Stellar, `feeInclusive`
- Exploit idea: Validation is format-only; bridge capability for account without trustline on Stellar is not encoded anywhere in the SDK. The intent is irrevocable once settled on intents.near.
- Invariant to test: validateAddress(s, Stellar) == true implies the hot bridge can deliver to s; otherwise the SDK must reject before signing.
- Expected Immunefi impact: High - withdrawal stuck or refunded to the wrong account until manual intervention (HackenProof: withdrawal processing; Immunefi class: temporary freezing of funds)
- Fast validation: vitest: assert `validateAddress('GA5ZSEJYB37JRC5AVCIA5MOP4RHTM335X2KGX3IHOJAPP5RE34K4KZVN', Chains.Stellar)`; cross-check the hot bridge's supported address types (live docs/API) and, if unsupported, this is a pre-sign validation gap.
