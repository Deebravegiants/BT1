# Q3507: Route confusion nep141:movement.omft.near + no `routeConfig` (default) (processWithdrawal)

## Question
With `assetId` = `nep141:movement.omft.near` (PoA native MOVE) and no `routeConfig` (default), can an unprivileged caller of `IntentsSDK.processWithdrawal` make bridge selection pick a bridge or destination chain that does not custody this token (because first bridge whose `supports()` is true wins, in order IntentsBridge, AuroraEngineBridge, PoaBridge, HotBridge, OmniBridge, DirectBridge), so the emitted `ft_withdraw`/`mt_withdraw`/`transfer` carries `receiver_id`/`recipient` for the wrong contract or chain and the funds are burned or stranded?

## Target
- File/function: packages/intents-sdk/src/sdk.ts `IntentsSDK.bridges` ordering, `createWithdrawalIntents`; bridge `supports()` / `parseAssetId()` in each bridges/*/ file
- Entrypoint: `IntentsSDK.processWithdrawal` (end-to-end: estimate -> validate -> sign -> publish -> wait)
- Attacker controls: `assetId`, `routeConfig` (no `routeConfig` (default)), `destinationAddress`
- Exploit idea: first bridge whose `supports()` is true wins, in order IntentsBridge, AuroraEngineBridge, PoaBridge, HotBridge, OmniBridge, DirectBridge. Token specifics: PoA native MOVE.
- Invariant to test: The bridge contract and chain named by the produced intent must equal the custodian of `nep141:movement.omft.near` and the chain the caller named; a mismatch must throw, never fall through to the next bridge.
- Expected Immunefi impact: Critical - funds delivered to a wrong address/chain/contract with no recovery (HackenProof: cross-chain address validation / withdrawal processing; Immunefi class: direct theft or permanent loss of user funds)
- Fast validation: vitest: construct IntentsSDK with mocked RPC/HTTP, call `IntentsSDK.processWithdrawal` with `nep141:movement.omft.near` and no `routeConfig` (default), assert `bridge.route` and the intent's `receiver_id`/`recipient`/chain.
