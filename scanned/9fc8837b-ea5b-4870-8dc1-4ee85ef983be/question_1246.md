# Q1246: Zcash transparent P2SH `t3...` on OmniBridge feeInclusive: false

## Question
For a Zcash withdrawal over OmniBridge with `feeInclusive: false`, `validateAddress` accepts a transparent P2SH `t3...` such as `t3Vz22vK5z2LcKEdg16Yv4FFneEL1zg9ojd` (format check only, as the docstring admits). Does `deriveOmniWithdrawIntentParams` -> `ft_withdraw` to `omni.bridge.near` with `msg.recipient = omniAddress(chainKind, address)` hand this address type to the Omni Bridge connector on the destination chain which cannot or will not pay that script/account type, so the tokens leave the user's intents balance, the bridge cannot deliver, and nothing in `describeWithdrawal` surfaces the failure?

## Target
- File/function: packages/intents-sdk/src/lib/validateAddress.ts `validateZcashAddress`; packages/intents-sdk/src/bridges/omni-bridge/omni-bridge.ts `validateWithdrawal`, `createWithdrawalIntents`, `describeWithdrawal`
- Entrypoint: `IntentsSDK.processWithdrawal` / `createWithdrawalIntents`
- Attacker controls: `destinationAddress` = `t3Vz22vK5z2LcKEdg16Yv4FFneEL1zg9ojd` (transparent P2SH `t3...`), `assetId` for Zcash, `feeInclusive`
- Exploit idea: Validation is format-only; bridge capability for transparent P2SH `t3...` on Zcash is not encoded anywhere in the SDK. The intent is irrevocable once settled on intents.near.
- Invariant to test: validateAddress(s, Zcash) == true implies the omni bridge can deliver to s; otherwise the SDK must reject before signing.
- Expected Immunefi impact: High - withdrawal stuck or refunded to the wrong account until manual intervention (HackenProof: withdrawal processing; Immunefi class: temporary freezing of funds)
- Fast validation: vitest: assert `validateAddress('t3Vz22vK5z2LcKEdg16Yv4FFneEL1zg9ojd', Chains.Zcash)`; cross-check the omni bridge's supported address types (live docs/API) and, if unsupported, this is a pre-sign validation gap.
