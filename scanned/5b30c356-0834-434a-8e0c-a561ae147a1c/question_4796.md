# Q4796: Tron contract address (TRC-20 USDT) on PoaBridge feeInclusive: false

## Question
For a Tron withdrawal over PoaBridge with `feeInclusive: false`, `validateAddress` accepts a contract address (TRC-20 USDT) such as `TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t` (format check only, as the docstring admits). Does `createWithdrawIntentPrimitive` -> `ft_withdraw` to the `omft.near` token with memo `WITHDRAW_TO:<address>[:<memo>]` hand this address type to the PoA bridge relayer (bridge.chaindefuser.com) which cannot or will not pay that script/account type, so the tokens leave the user's intents balance, the bridge cannot deliver, and nothing in `describeWithdrawal` surfaces the failure?

## Target
- File/function: packages/intents-sdk/src/lib/validateAddress.ts `validateTronAddress`; packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts `validateWithdrawal`, `createWithdrawalIntents`, `describeWithdrawal`
- Entrypoint: `IntentsSDK.processWithdrawal` / `createWithdrawalIntents`
- Attacker controls: `destinationAddress` = `TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t` (contract address (TRC-20 USDT)), `assetId` for Tron, `feeInclusive`
- Exploit idea: Validation is format-only; bridge capability for contract address (TRC-20 USDT) on Tron is not encoded anywhere in the SDK. The intent is irrevocable once settled on intents.near.
- Invariant to test: validateAddress(s, Tron) == true implies the poa bridge can deliver to s; otherwise the SDK must reject before signing.
- Expected Immunefi impact: High - withdrawal stuck or refunded to the wrong account until manual intervention (HackenProof: withdrawal processing; Immunefi class: temporary freezing of funds)
- Fast validation: vitest: assert `validateAddress('TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t', Chains.Tron)`; cross-check the poa bridge's supported address types (live docs/API) and, if unsupported, this is a pre-sign validation gap.
