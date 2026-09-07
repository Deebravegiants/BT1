# Q4435: Dash P2SH `7...` on PoaBridge feeInclusive: true

## Question
For a Dash withdrawal over PoaBridge with `feeInclusive: true`, `validateAddress` accepts a P2SH `7...` such as `7XmxQZRjjZ9nmzYsaH7yhC3bJvyDFYkuTz` (format check only, as the docstring admits). Does `createWithdrawIntentPrimitive` -> `ft_withdraw` to the `omft.near` token with memo `WITHDRAW_TO:<address>[:<memo>]` hand this address type to the PoA bridge relayer (bridge.chaindefuser.com) which cannot or will not pay that script/account type, so the tokens leave the user's intents balance, the bridge cannot deliver, and nothing in `describeWithdrawal` surfaces the failure?

## Target
- File/function: packages/intents-sdk/src/lib/validateAddress.ts `validateDashAddress`; packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts `validateWithdrawal`, `createWithdrawalIntents`, `describeWithdrawal`
- Entrypoint: `IntentsSDK.processWithdrawal` / `createWithdrawalIntents`
- Attacker controls: `destinationAddress` = `7XmxQZRjjZ9nmzYsaH7yhC3bJvyDFYkuTz` (P2SH `7...`), `assetId` for Dash, `feeInclusive`
- Exploit idea: Validation is format-only; bridge capability for P2SH `7...` on Dash is not encoded anywhere in the SDK. The intent is irrevocable once settled on intents.near.
- Invariant to test: validateAddress(s, Dash) == true implies the poa bridge can deliver to s; otherwise the SDK must reject before signing.
- Expected Immunefi impact: High - withdrawal stuck or refunded to the wrong account until manual intervention (HackenProof: withdrawal processing; Immunefi class: temporary freezing of funds)
- Fast validation: vitest: assert `validateAddress('7XmxQZRjjZ9nmzYsaH7yhC3bJvyDFYkuTz', Chains.Dash)`; cross-check the poa bridge's supported address types (live docs/API) and, if unsupported, this is a pre-sign validation gap.
