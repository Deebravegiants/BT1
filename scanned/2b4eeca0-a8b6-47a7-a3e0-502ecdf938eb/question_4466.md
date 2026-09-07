# Q4466: Route confusion nep141:aptos.omft.near + `createNearWithdrawalRoute(msg)` w (createWithdrawalIntents)

## Question
With `assetId` = `nep141:aptos.omft.near` (MIGRATED to Omni (ChainKind.Aptos)) and `createNearWithdrawalRoute(msg)` with an attacker-chosen `msg`, can an unprivileged caller of `IntentsSDK.createWithdrawalIntents` make bridge selection pick a bridge or destination chain that does not custody this token (because `DirectBridge` forwards `msg` into `ft_withdraw`, turning it into `ft_transfer_call` on `receiver_id`), so the emitted `ft_withdraw`/`mt_withdraw`/`transfer` carries `receiver_id`/`recipient` for the wrong contract or chain and the funds are burned or stranded?

## Target
- File/function: packages/intents-sdk/src/sdk.ts `IntentsSDK.bridges` ordering, `createWithdrawalIntents`; bridge `supports()` / `parseAssetId()` in each bridges/*/ file
- Entrypoint: `IntentsSDK.createWithdrawalIntents` (returns raw `IntentPrimitive[]` for the integrator to sign with any signer)
- Attacker controls: `assetId`, `routeConfig` (`createNearWithdrawalRoute(msg)` with an attacker-chosen `msg`), `destinationAddress`
- Exploit idea: `DirectBridge` forwards `msg` into `ft_withdraw`, turning it into `ft_transfer_call` on `receiver_id`. Token specifics: MIGRATED to Omni (ChainKind.Aptos).
- Invariant to test: The bridge contract and chain named by the produced intent must equal the custodian of `nep141:aptos.omft.near` and the chain the caller named; a mismatch must throw, never fall through to the next bridge.
- Expected Immunefi impact: Critical - funds delivered to a wrong address/chain/contract with no recovery (HackenProof: cross-chain address validation / withdrawal processing; Immunefi class: direct theft or permanent loss of user funds)
- Fast validation: vitest: construct IntentsSDK with mocked RPC/HTTP, call `IntentsSDK.createWithdrawalIntents` with `nep141:aptos.omft.near` and `createNearWithdrawalRoute(msg)` with an attacker-chosen `msg`, assert `bridge.route` and the intent's `receiver_id`/`recipient`/chain.
