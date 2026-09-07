# Q2851: Route confusion nep141:gnosis-0xe91d153e0b41518a2ce8dd3d + `createInternalTransferRoute()` (processWithdrawal)

## Question
With `assetId` = `nep141:gnosis-0xe91d153e0b41518a2ce8dd3d7944fa863463a97d.omft.near` (PoA ERC-20 on Gnosis) and `createInternalTransferRoute()`, can an unprivileged caller of `IntentsSDK.processWithdrawal` make bridge selection pick a bridge or destination chain that does not custody this token (because `IntentsBridge` emits `transfer` to any `receiver_id` with no asset checks), so the emitted `ft_withdraw`/`mt_withdraw`/`transfer` carries `receiver_id`/`recipient` for the wrong contract or chain and the funds are burned or stranded?

## Target
- File/function: packages/intents-sdk/src/sdk.ts `IntentsSDK.bridges` ordering, `createWithdrawalIntents`; bridge `supports()` / `parseAssetId()` in each bridges/*/ file
- Entrypoint: `IntentsSDK.processWithdrawal` (end-to-end: estimate -> validate -> sign -> publish -> wait)
- Attacker controls: `assetId`, `routeConfig` (`createInternalTransferRoute()`), `destinationAddress`
- Exploit idea: `IntentsBridge` emits `transfer` to any `receiver_id` with no asset checks. Token specifics: PoA ERC-20 on Gnosis.
- Invariant to test: The bridge contract and chain named by the produced intent must equal the custodian of `nep141:gnosis-0xe91d153e0b41518a2ce8dd3d7944fa863463a97d.omft.near` and the chain the caller named; a mismatch must throw, never fall through to the next bridge.
- Expected Immunefi impact: Critical - funds delivered to a wrong address/chain/contract with no recovery (HackenProof: cross-chain address validation / withdrawal processing; Immunefi class: direct theft or permanent loss of user funds)
- Fast validation: vitest: construct IntentsSDK with mocked RPC/HTTP, call `IntentsSDK.processWithdrawal` with `nep141:gnosis-0xe91d153e0b41518a2ce8dd3d7944fa863463a97d.omft.near` and `createInternalTransferRoute()`, assert `bridge.route` and the intent's `receiver_id`/`recipient`/chain.
