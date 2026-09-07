# Q2807: Route confusion nep141:gnosis-0xe91d153e0b41518a2ce8dd3d + `createOmniBridgeRoute(chain)` nam (createWithdrawalIntents)

## Question
Trace `IntentsSDK.createWithdrawalIntents` for `nep141:gnosis-0xe91d153e0b41518a2ce8dd3d7944fa863463a97d.omft.near` (PoA ERC-20 on Gnosis) under `createOmniBridgeRoute(chain)` naming a different chain than the token's origin: `OmniBridge.supports` accepts any nep141 once `routeConfig.chain` is set and only checks `getBridgedToken` != null. Can an unprivileged caller obtain a signed `IntentPrimitive[]` whose `receiver_id`/`recipient`/chain does not match the token's real bridge, without any bridge throwing, and does the SDK then report `completed`?

## Target
- File/function: packages/intents-sdk/src/sdk.ts `IntentsSDK.bridges` ordering, `createWithdrawalIntents`; bridge `supports()` / `parseAssetId()` in each bridges/*/ file
- Entrypoint: `IntentsSDK.createWithdrawalIntents` (returns raw `IntentPrimitive[]` for the integrator to sign with any signer)
- Attacker controls: `assetId`, `routeConfig` (`createOmniBridgeRoute(chain)` naming a different chain than the token's origin), `destinationAddress`
- Exploit idea: `OmniBridge.supports` accepts any nep141 once `routeConfig.chain` is set and only checks `getBridgedToken` != null. Token specifics: PoA ERC-20 on Gnosis.
- Invariant to test: The bridge contract and chain named by the produced intent must equal the custodian of `nep141:gnosis-0xe91d153e0b41518a2ce8dd3d7944fa863463a97d.omft.near` and the chain the caller named; a mismatch must throw, never fall through to the next bridge.
- Expected Immunefi impact: Critical - funds delivered to a wrong address/chain/contract with no recovery (HackenProof: cross-chain address validation / withdrawal processing; Immunefi class: direct theft or permanent loss of user funds)
- Fast validation: vitest: construct IntentsSDK with mocked RPC/HTTP, call `IntentsSDK.createWithdrawalIntents` with `nep141:gnosis-0xe91d153e0b41518a2ce8dd3d7944fa863463a97d.omft.near` and `createOmniBridgeRoute(chain)` naming a different chain than the token's origin, assert `bridge.route` and the intent's `receiver_id`/`recipient`/chain.
