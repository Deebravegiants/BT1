# Q1953: Fogo token account instead of owner on OmniBridge feeInclusive: false

## Question
For a Fogo withdrawal over OmniBridge with `feeInclusive: false`, `validateAddress` accepts a token account instead of owner such as `7UX2i7SucgLMQcfZ75s3VXmZZY4YRUyJN9X1RgfMoDUi` (format check only, as the docstring admits). Does `deriveOmniWithdrawIntentParams` -> `ft_withdraw` to `omni.bridge.near` with `msg.recipient = omniAddress(chainKind, address)` hand this address type to the Omni Bridge connector on the destination chain which cannot or will not pay that script/account type, so the tokens leave the user's intents balance, the bridge cannot deliver, and nothing in `describeWithdrawal` surfaces the failure?

## Target
- File/function: packages/intents-sdk/src/lib/validateAddress.ts `validateSolAddress`; packages/intents-sdk/src/bridges/omni-bridge/omni-bridge.ts `validateWithdrawal`, `createWithdrawalIntents`, `describeWithdrawal`
- Entrypoint: `IntentsSDK.processWithdrawal` / `createWithdrawalIntents`
- Attacker controls: `destinationAddress` = `7UX2i7SucgLMQcfZ75s3VXmZZY4YRUyJN9X1RgfMoDUi` (token account instead of owner), `assetId` for Fogo, `feeInclusive`
- Exploit idea: Validation is format-only; bridge capability for token account instead of owner on Fogo is not encoded anywhere in the SDK. The intent is irrevocable once settled on intents.near.
- Invariant to test: validateAddress(s, Fogo) == true implies the omni bridge can deliver to s; otherwise the SDK must reject before signing.
- Expected Immunefi impact: High - withdrawal stuck or refunded to the wrong account until manual intervention (HackenProof: withdrawal processing; Immunefi class: temporary freezing of funds)
- Fast validation: vitest: assert `validateAddress('7UX2i7SucgLMQcfZ75s3VXmZZY4YRUyJN9X1RgfMoDUi', Chains.Fogo)`; cross-check the omni bridge's supported address types (live docs/API) and, if unsupported, this is a pre-sign validation gap.
