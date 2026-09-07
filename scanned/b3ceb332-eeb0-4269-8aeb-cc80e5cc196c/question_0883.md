# Q0883: Zcash TEX `tex1...` on OmniBridge feeInclusive: true

## Question
For a Zcash withdrawal over OmniBridge with `feeInclusive: true`, `validateAddress` accepts a TEX `tex1...` such as `tex1s2rt77ggv6q989lr49rkgzmh5slsksa9khdgte` (format check only, as the docstring admits). Does `deriveOmniWithdrawIntentParams` -> `ft_withdraw` to `omni.bridge.near` with `msg.recipient = omniAddress(chainKind, address)` hand this address type to the Omni Bridge connector on the destination chain which cannot or will not pay that script/account type, so the tokens leave the user's intents balance, the bridge cannot deliver, and nothing in `describeWithdrawal` surfaces the failure?

## Target
- File/function: packages/intents-sdk/src/lib/validateAddress.ts `validateZcashAddress`; packages/intents-sdk/src/bridges/omni-bridge/omni-bridge.ts `validateWithdrawal`, `createWithdrawalIntents`, `describeWithdrawal`
- Entrypoint: `IntentsSDK.processWithdrawal` / `createWithdrawalIntents`
- Attacker controls: `destinationAddress` = `tex1s2rt77ggv6q989lr49rkgzmh5slsksa9khdgte` (TEX `tex1...`), `assetId` for Zcash, `feeInclusive`
- Exploit idea: Validation is format-only; bridge capability for TEX `tex1...` on Zcash is not encoded anywhere in the SDK. The intent is irrevocable once settled on intents.near.
- Invariant to test: validateAddress(s, Zcash) == true implies the omni bridge can deliver to s; otherwise the SDK must reject before signing.
- Expected Immunefi impact: High - withdrawal stuck or refunded to the wrong account until manual intervention (HackenProof: withdrawal processing; Immunefi class: temporary freezing of funds)
- Fast validation: vitest: assert `validateAddress('tex1s2rt77ggv6q989lr49rkgzmh5slsksa9khdgte', Chains.Zcash)`; cross-check the omni bridge's supported address types (live docs/API) and, if unsupported, this is a pre-sign validation gap.
