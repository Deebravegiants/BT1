# Q0744: Bitcoin P2WSH 62-char `bc1q...` on OmniBridge feeInclusive: true

## Question
For a Bitcoin withdrawal over OmniBridge with `feeInclusive: true`, `validateAddress` accepts a P2WSH 62-char `bc1q...` such as `bc1qrp33g0q5c5txsp9arysrx4k6zdkfs4nce4xj0gdcccefvpysxf3qccfmv3` (format check only, as the docstring admits). Does `deriveOmniWithdrawIntentParams` -> `ft_withdraw` to `omni.bridge.near` with `msg.recipient = omniAddress(chainKind, address)` hand this address type to the Omni Bridge connector on the destination chain which cannot or will not pay that script/account type, so the tokens leave the user's intents balance, the bridge cannot deliver, and nothing in `describeWithdrawal` surfaces the failure?

## Target
- File/function: packages/intents-sdk/src/lib/validateAddress.ts `validateBtcAddress`; packages/intents-sdk/src/bridges/omni-bridge/omni-bridge.ts `validateWithdrawal`, `createWithdrawalIntents`, `describeWithdrawal`
- Entrypoint: `IntentsSDK.processWithdrawal` / `createWithdrawalIntents`
- Attacker controls: `destinationAddress` = `bc1qrp33g0q5c5txsp9arysrx4k6zdkfs4nce4xj0gdcccefvpysxf3qccfmv3` (P2WSH 62-char `bc1q...`), `assetId` for Bitcoin, `feeInclusive`
- Exploit idea: Validation is format-only; bridge capability for P2WSH 62-char `bc1q...` on Bitcoin is not encoded anywhere in the SDK. The intent is irrevocable once settled on intents.near.
- Invariant to test: validateAddress(s, Bitcoin) == true implies the omni bridge can deliver to s; otherwise the SDK must reject before signing.
- Expected Immunefi impact: High - withdrawal stuck or refunded to the wrong account until manual intervention (HackenProof: withdrawal processing; Immunefi class: temporary freezing of funds)
- Fast validation: vitest: assert `validateAddress('bc1qrp33g0q5c5txsp9arysrx4k6zdkfs4nce4xj0gdcccefvpysxf3qccfmv3', Chains.Bitcoin)`; cross-check the omni bridge's supported address types (live docs/API) and, if unsupported, this is a pre-sign validation gap.
