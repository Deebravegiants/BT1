# Q1670: Solana program id on OmniBridge feeInclusive: false

## Question
For a Solana withdrawal over OmniBridge with `feeInclusive: false`, `validateAddress` accepts a program id such as `TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA` (format check only, as the docstring admits). Does `deriveOmniWithdrawIntentParams` -> `ft_withdraw` to `omni.bridge.near` with `msg.recipient = omniAddress(chainKind, address)` hand this address type to the Omni Bridge connector on the destination chain which cannot or will not pay that script/account type, so the tokens leave the user's intents balance, the bridge cannot deliver, and nothing in `describeWithdrawal` surfaces the failure?

## Target
- File/function: packages/intents-sdk/src/lib/validateAddress.ts `validateSolAddress`; packages/intents-sdk/src/bridges/omni-bridge/omni-bridge.ts `validateWithdrawal`, `createWithdrawalIntents`, `describeWithdrawal`
- Entrypoint: `IntentsSDK.processWithdrawal` / `createWithdrawalIntents`
- Attacker controls: `destinationAddress` = `TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA` (program id), `assetId` for Solana, `feeInclusive`
- Exploit idea: Validation is format-only; bridge capability for program id on Solana is not encoded anywhere in the SDK. The intent is irrevocable once settled on intents.near.
- Invariant to test: validateAddress(s, Solana) == true implies the omni bridge can deliver to s; otherwise the SDK must reject before signing.
- Expected Immunefi impact: High - withdrawal stuck or refunded to the wrong account until manual intervention (HackenProof: withdrawal processing; Immunefi class: temporary freezing of funds)
- Fast validation: vitest: assert `validateAddress('TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', Chains.Solana)`; cross-check the omni bridge's supported address types (live docs/API) and, if unsupported, this is a pre-sign validation gap.
