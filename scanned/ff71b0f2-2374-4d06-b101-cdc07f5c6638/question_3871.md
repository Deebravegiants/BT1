# Q3871: BitcoinCash CashAddr P2SH `p...` on PoaBridge feeInclusive: true

## Question
For a BitcoinCash withdrawal over PoaBridge with `feeInclusive: true`, `validateAddress` accepts a CashAddr P2SH `p...` such as `bitcoincash:pr6m7j9njldwwzlg9v7v53unlr4jkmx6eylep8ekg2` (format check only, as the docstring admits). Does `createWithdrawIntentPrimitive` -> `ft_withdraw` to the `omft.near` token with memo `WITHDRAW_TO:<address>[:<memo>]` hand this address type to the PoA bridge relayer (bridge.chaindefuser.com) which cannot or will not pay that script/account type, so the tokens leave the user's intents balance, the bridge cannot deliver, and nothing in `describeWithdrawal` surfaces the failure?

## Target
- File/function: packages/intents-sdk/src/lib/validateAddress.ts `validateBchAddress`; packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts `validateWithdrawal`, `createWithdrawalIntents`, `describeWithdrawal`
- Entrypoint: `IntentsSDK.processWithdrawal` / `createWithdrawalIntents`
- Attacker controls: `destinationAddress` = `bitcoincash:pr6m7j9njldwwzlg9v7v53unlr4jkmx6eylep8ekg2` (CashAddr P2SH `p...`), `assetId` for BitcoinCash, `feeInclusive`
- Exploit idea: Validation is format-only; bridge capability for CashAddr P2SH `p...` on BitcoinCash is not encoded anywhere in the SDK. The intent is irrevocable once settled on intents.near.
- Invariant to test: validateAddress(s, BitcoinCash) == true implies the poa bridge can deliver to s; otherwise the SDK must reject before signing.
- Expected Immunefi impact: High - withdrawal stuck or refunded to the wrong account until manual intervention (HackenProof: withdrawal processing; Immunefi class: temporary freezing of funds)
- Fast validation: vitest: assert `validateAddress('bitcoincash:pr6m7j9njldwwzlg9v7v53unlr4jkmx6eylep8ekg2', Chains.BitcoinCash)`; cross-check the poa bridge's supported address types (live docs/API) and, if unsupported, this is a pre-sign validation gap.
