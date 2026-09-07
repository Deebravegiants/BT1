# Q5818: Cardano enterprise address type 6 via PoaBridge (processWithdrawal)

## Question
Can an unprivileged user enter through `IntentsSDK.processWithdrawal` on the PoaBridge route for Cardano with `destinationAddress` = `addr1v9ylzsgxaa6xctf4juup682ar3juj85n8tx3hthnljg47zc9cd0an` (enterprise address type 6) and make `validateAddress` (`validateCardanoAddress`) accept a string that `createWithdrawIntentPrimitive` -> `ft_withdraw` to the `omft.near` token with memo `WITHDRAW_TO:<address>[:<memo>]` then forwards unchanged, so the address the PoA bridge relayer (bridge.chaindefuser.com) pays differs from the account the user controls and the withdrawal is lost?

## Target
- File/function: packages/intents-sdk/src/lib/validateAddress.ts `validateCardanoAddress`; packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts `validateWithdrawal` / `createWithdrawalIntents`
- Entrypoint: `IntentsSDK.processWithdrawal` (end-to-end: estimate -> validate -> sign -> publish -> wait)
- Attacker controls: `destinationAddress` string (`addr1v9ylzsgxaa6xctf4juup682ar3juj85n8tx3hthnljg47zc9cd0an`), `assetId` for a Cardano poa token, `destinationMemo`
- Exploit idea: type 0..7 accepted; script addresses (types 1,3,5,7) may be unspendable. Encoding path: `createWithdrawIntentPrimitive` -> `ft_withdraw` to the `omft.near` token with memo `WITHDRAW_TO:<address>[:<memo>]`.
- Invariant to test: For every string s where `validateAddress(s, 'cip34:1-764824073')` is true, the payout address derived by the PoA bridge relayer (bridge.chaindefuser.com) from the emitted intent must be the same account as s. Test: run validateAddress + createWithdrawalIntents on `addr1v9ylzsgxaa6xctf4juup682ar3juj85n8tx3hthnljg47zc9cd0an` and inspect the emitted memo/recipient/receiver.
- Expected Immunefi impact: Critical - funds delivered to a wrong address/chain/contract with no recovery (HackenProof: cross-chain address validation / withdrawal processing; Immunefi class: direct theft or permanent loss of user funds)
- Fast validation: vitest: call `validateAddress('addr1v9ylzsgxaa6xctf4juup682ar3juj85n8tx3hthnljg47zc9cd0an', Chains.Cardano)`; then `createWithdrawalIntents` with mocked fee and assert the encoded destination byte-for-byte; compare against the poa bridge's documented accepted format.
