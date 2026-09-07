# Q1316: Route confusion nep141:doge.omft.near + `createNearWithdrawalRoute(msg)` w (processWithdrawal)

## Question
With `assetId` = `nep141:doge.omft.near` (PoA native Doge) and `createNearWithdrawalRoute(msg)` with an attacker-chosen `msg`, can an unprivileged caller of `IntentsSDK.processWithdrawal` make bridge selection pick a bridge or destination chain that does not custody this token (because `DirectBridge` forwards `msg` into `ft_withdraw`, turning it into `ft_transfer_call` on `receiver_id`), so the emitted `ft_withdraw`/`mt_withdraw`/`transfer` carries `receiver_id`/`recipient` for the wrong contract or chain and the funds are burned or stranded?

## Target
- File/function: packages/intents-sdk/src/sdk.ts `IntentsSDK.bridges` ordering, `createWithdrawalIntents`; bridge `supports()` / `parseAssetId()` in each bridges/*/ file
- Entrypoint: `IntentsSDK.processWithdrawal` (end-to-end: estimate -> validate -> sign -> publish -> wait)
- Attacker controls: `assetId`, `routeConfig` (`createNearWithdrawalRoute(msg)` with an attacker-chosen `msg`), `destinationAddress`
- Exploit idea: `DirectBridge` forwards `msg` into `ft_withdraw`, turning it into `ft_transfer_call` on `receiver_id`. Token specifics: PoA native Doge.
- Invariant to test: The bridge contract and chain named by the produced intent must equal the custodian of `nep141:doge.omft.near` and the chain the caller named; a mismatch must throw, never fall through to the next bridge.
- Expected Immunefi impact: Critical - funds delivered to a wrong address/chain/contract with no recovery (HackenProof: cross-chain address validation / withdrawal processing; Immunefi class: direct theft or permanent loss of user funds)
- Fast validation: vitest: construct IntentsSDK with mocked RPC/HTTP, call `IntentsSDK.processWithdrawal` with `nep141:doge.omft.near` and `createNearWithdrawalRoute(msg)` with an attacker-chosen `msg`, assert `bridge.route` and the intent's `receiver_id`/`recipient`/chain.
