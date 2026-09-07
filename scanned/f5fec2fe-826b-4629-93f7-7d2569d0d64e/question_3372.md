# Q3372: Cardano enterprise address (type 6) on PoaBridge feeInclusive: false

## Question
For a Cardano withdrawal over PoaBridge with `feeInclusive: false`, `validateAddress` accepts a enterprise address (type 6) such as `addr1v9ylzsgxaa6xctf4juup682ar3juj85n8tx3hthnljg47zc9cd0an` (format check only, as the docstring admits). Does `createWithdrawIntentPrimitive` -> `ft_withdraw` to the `omft.near` token with memo `WITHDRAW_TO:<address>[:<memo>]` hand this address type to the PoA bridge relayer (bridge.chaindefuser.com) which cannot or will not pay that script/account type, so the tokens leave the user's intents balance, the bridge cannot deliver, and nothing in `describeWithdrawal` surfaces the failure?

## Target
- File/function: packages/intents-sdk/src/lib/validateAddress.ts `validateCardanoAddress`; packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts `validateWithdrawal`, `createWithdrawalIntents`, `describeWithdrawal`
- Entrypoint: `IntentsSDK.processWithdrawal` / `createWithdrawalIntents`
- Attacker controls: `destinationAddress` = `addr1v9ylzsgxaa6xctf4juup682ar3juj85n8tx3hthnljg47zc9cd0an` (enterprise address (type 6)), `assetId` for Cardano, `feeInclusive`
- Exploit idea: Validation is format-only; bridge capability for enterprise address (type 6) on Cardano is not encoded anywhere in the SDK. The intent is irrevocable once settled on intents.near.
- Invariant to test: validateAddress(s, Cardano) == true implies the poa bridge can deliver to s; otherwise the SDK must reject before signing.
- Expected Immunefi impact: High - withdrawal stuck or refunded to the wrong account until manual intervention (HackenProof: withdrawal processing; Immunefi class: temporary freezing of funds)
- Fast validation: vitest: assert `validateAddress('addr1v9ylzsgxaa6xctf4juup682ar3juj85n8tx3hthnljg47zc9cd0an', Chains.Cardano)`; cross-check the poa bridge's supported address types (live docs/API) and, if unsupported, this is a pre-sign validation gap.
