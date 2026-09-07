# Q3582: Litecoin taproot `ltc1p...` on PoaBridge feeInclusive: true

## Question
For a Litecoin withdrawal over PoaBridge with `feeInclusive: true`, `validateAddress` accepts a taproot `ltc1p...` such as `ltc1pqar0srrr7xfkvy5l643lydnw9re59gtzzwf5mdq2ka6yp` (format check only, as the docstring admits). Does `createWithdrawIntentPrimitive` -> `ft_withdraw` to the `omft.near` token with memo `WITHDRAW_TO:<address>[:<memo>]` hand this address type to the PoA bridge relayer (bridge.chaindefuser.com) which cannot or will not pay that script/account type, so the tokens leave the user's intents balance, the bridge cannot deliver, and nothing in `describeWithdrawal` surfaces the failure?

## Target
- File/function: packages/intents-sdk/src/lib/validateAddress.ts `validateLitecoinAddress`; packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts `validateWithdrawal`, `createWithdrawalIntents`, `describeWithdrawal`
- Entrypoint: `IntentsSDK.processWithdrawal` / `createWithdrawalIntents`
- Attacker controls: `destinationAddress` = `ltc1pqar0srrr7xfkvy5l643lydnw9re59gtzzwf5mdq2ka6yp` (taproot `ltc1p...`), `assetId` for Litecoin, `feeInclusive`
- Exploit idea: Validation is format-only; bridge capability for taproot `ltc1p...` on Litecoin is not encoded anywhere in the SDK. The intent is irrevocable once settled on intents.near.
- Invariant to test: validateAddress(s, Litecoin) == true implies the poa bridge can deliver to s; otherwise the SDK must reject before signing.
- Expected Immunefi impact: High - withdrawal stuck or refunded to the wrong account until manual intervention (HackenProof: withdrawal processing; Immunefi class: temporary freezing of funds)
- Fast validation: vitest: assert `validateAddress('ltc1pqar0srrr7xfkvy5l643lydnw9re59gtzzwf5mdq2ka6yp', Chains.Litecoin)`; cross-check the poa bridge's supported address types (live docs/API) and, if unsupported, this is a pre-sign validation gap.
