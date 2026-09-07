# Q5114: XRPL unfunded account for an issued token via PoaBridge (createWithdrawalIntents)

## Question
Can an unprivileged user enter through `IntentsSDK.createWithdrawalIntents` on the PoaBridge route for XRPL with `destinationAddress` = `rNewUnfundedAccount111111111111111` (unfunded account for an issued token) and make `validateAddress` (`validateXrpAddress`) accept a string that `createWithdrawIntentPrimitive` -> `ft_withdraw` to the `omft.near` token with memo `WITHDRAW_TO:<address>[:<memo>]` then forwards unchanged, so the address the PoA bridge relayer (bridge.chaindefuser.com) pays differs from the account the user controls and the withdrawal is lost?

## Target
- File/function: packages/intents-sdk/src/lib/validateAddress.ts `validateXrpAddress`; packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts `validateWithdrawal` / `createWithdrawalIntents`
- Entrypoint: `IntentsSDK.createWithdrawalIntents` (returns raw `IntentPrimitive[]` for the integrator to sign with any signer)
- Attacker controls: `destinationAddress` string (`rNewUnfundedAccount111111111111111`), `assetId` for a XRPL poa token, `destinationMemo`
- Exploit idea: `XrplAccountNotFundedError` is swallowed only for XRP; but does the check run at all when `getAccountInfo` fails for other reasons?. Encoding path: `createWithdrawIntentPrimitive` -> `ft_withdraw` to the `omft.near` token with memo `WITHDRAW_TO:<address>[:<memo>]`.
- Invariant to test: For every string s where `validateAddress(s, 'xrpl:0')` is true, the payout address derived by the PoA bridge relayer (bridge.chaindefuser.com) from the emitted intent must be the same account as s. Test: run validateAddress + createWithdrawalIntents on `rNewUnfundedAccount111111111111111` and inspect the emitted memo/recipient/receiver.
- Expected Immunefi impact: Critical - funds delivered to a wrong address/chain/contract with no recovery (HackenProof: cross-chain address validation / withdrawal processing; Immunefi class: direct theft or permanent loss of user funds)
- Fast validation: vitest: call `validateAddress('rNewUnfundedAccount111111111111111', Chains.XRPL)`; then `createWithdrawalIntents` with mocked fee and assert the encoded destination byte-for-byte; compare against the poa bridge's documented accepted format.
