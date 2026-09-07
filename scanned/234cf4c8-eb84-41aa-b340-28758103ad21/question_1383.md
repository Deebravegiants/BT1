# Q1383: Solana PDA / off-curve on OmniBridge feeInclusive: false

## Question
For a Solana withdrawal over OmniBridge with `feeInclusive: false`, `validateAddress` accepts a PDA / off-curve such as `9xQeWvG816bUx9EPjHmaT23yvVM2ZWbrrpZb9PusVFin` (format check only, as the docstring admits). Does `deriveOmniWithdrawIntentParams` -> `ft_withdraw` to `omni.bridge.near` with `msg.recipient = omniAddress(chainKind, address)` hand this address type to the Omni Bridge connector on the destination chain which cannot or will not pay that script/account type, so the tokens leave the user's intents balance, the bridge cannot deliver, and nothing in `describeWithdrawal` surfaces the failure?

## Target
- File/function: packages/intents-sdk/src/lib/validateAddress.ts `validateSolAddress`; packages/intents-sdk/src/bridges/omni-bridge/omni-bridge.ts `validateWithdrawal`, `createWithdrawalIntents`, `describeWithdrawal`
- Entrypoint: `IntentsSDK.processWithdrawal` / `createWithdrawalIntents`
- Attacker controls: `destinationAddress` = `9xQeWvG816bUx9EPjHmaT23yvVM2ZWbrrpZb9PusVFin` (PDA / off-curve), `assetId` for Solana, `feeInclusive`
- Exploit idea: Validation is format-only; bridge capability for PDA / off-curve on Solana is not encoded anywhere in the SDK. The intent is irrevocable once settled on intents.near.
- Invariant to test: validateAddress(s, Solana) == true implies the omni bridge can deliver to s; otherwise the SDK must reject before signing.
- Expected Immunefi impact: High - withdrawal stuck or refunded to the wrong account until manual intervention (HackenProof: withdrawal processing; Immunefi class: temporary freezing of funds)
- Fast validation: vitest: assert `validateAddress('9xQeWvG816bUx9EPjHmaT23yvVM2ZWbrrpZb9PusVFin', Chains.Solana)`; cross-check the omni bridge's supported address types (live docs/API) and, if unsupported, this is a pre-sign validation gap.
