# Q5004: Aptos account without CoinStore registered on OmniBridge feeInclusive: true

## Question
For a Aptos withdrawal over OmniBridge with `feeInclusive: true`, `validateAddress` accepts a account without CoinStore registered such as `0x1111111111111111111111111111111111111111111111111111111111111111` (format check only, as the docstring admits). Does `deriveOmniWithdrawIntentParams` -> `ft_withdraw` to `omni.bridge.near` with `msg.recipient = omniAddress(chainKind, address)` hand this address type to the Omni Bridge connector on the destination chain which cannot or will not pay that script/account type, so the tokens leave the user's intents balance, the bridge cannot deliver, and nothing in `describeWithdrawal` surfaces the failure?

## Target
- File/function: packages/intents-sdk/src/lib/validateAddress.ts `validateAptosAddress`; packages/intents-sdk/src/bridges/omni-bridge/omni-bridge.ts `validateWithdrawal`, `createWithdrawalIntents`, `describeWithdrawal`
- Entrypoint: `IntentsSDK.processWithdrawal` / `createWithdrawalIntents`
- Attacker controls: `destinationAddress` = `0x1111111111111111111111111111111111111111111111111111111111111111` (account without CoinStore registered), `assetId` for Aptos, `feeInclusive`
- Exploit idea: Validation is format-only; bridge capability for account without CoinStore registered on Aptos is not encoded anywhere in the SDK. The intent is irrevocable once settled on intents.near.
- Invariant to test: validateAddress(s, Aptos) == true implies the omni bridge can deliver to s; otherwise the SDK must reject before signing.
- Expected Immunefi impact: High - withdrawal stuck or refunded to the wrong account until manual intervention (HackenProof: withdrawal processing; Immunefi class: temporary freezing of funds)
- Fast validation: vitest: assert `validateAddress('0x1111111111111111111111111111111111111111111111111111111111111111', Chains.Aptos)`; cross-check the omni bridge's supported address types (live docs/API) and, if unsupported, this is a pre-sign validation gap.
