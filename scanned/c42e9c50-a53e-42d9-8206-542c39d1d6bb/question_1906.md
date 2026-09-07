# Q1906: Contract binding nep413: a custom `EnvConfig.contractID` with a t

## Question
When a custom `EnvConfig.contractID` with a typo, for `nep413`, does the SDK sign a payload whose `verifying_contract`/`recipient` binds it to a contract other than `envConfig.contractID` used by `IntentRelayerPublic`, so the relayer either rejects it after the user signed or a second deployment (staging/private shard) accepts the same signed intent?

## Target
- File/function: packages/intents-sdk/src/intents/intent-payload-builder.ts `setVerifyingContract`; intent-signer-nep413.ts (`recipient`); intent-signer-viem.ts; intent-relayer-public.ts `waitForSettlement` (accountId = contractID)
- Entrypoint: `IntentsSDK.intentBuilder()` / `signAndSendIntent`
- Attacker controls: `verifying_contract` override, `env` config
- Exploit idea: The builder documents the override as dangerous but nothing asserts consistency with the relayer's target; NEP-413 `recipient` is the only binding for that standard.
- Invariant to test: signed verifying_contract == recipient == envConfig.contractID.
- Expected Immunefi impact: High - signature bound to the wrong contract, signer or nonce (HackenProof: intent signing and verification, nonce management)
- Fast validation: vitest: build with override, sign, assert payload fields vs relayer target.
