# Q3730: Route confusion nep141:zec.omft.near + `createOmniBridgeRoute()` with no  (processWithdrawal)

## Question
With `assetId` = `nep141:zec.omft.near` (PoA-named token MIGRATED to Omni via `POA_TOKENS_MIGRATED_TO_OMNI_BRIDGE` (ChainKind.Zcash, UTXO chain)) and `createOmniBridgeRoute()` with no chain, can an unprivileged caller of `IntentsSDK.processWithdrawal` make bridge selection pick a bridge or destination chain that does not custody this token (because `OmniBridge.supports` requires a valid omni token or migrated PoA token, throws otherwise), so the emitted `ft_withdraw`/`mt_withdraw`/`transfer` carries `receiver_id`/`recipient` for the wrong contract or chain and the funds are burned or stranded?

## Target
- File/function: packages/intents-sdk/src/sdk.ts `IntentsSDK.bridges` ordering, `createWithdrawalIntents`; bridge `supports()` / `parseAssetId()` in each bridges/*/ file
- Entrypoint: `IntentsSDK.processWithdrawal` (end-to-end: estimate -> validate -> sign -> publish -> wait)
- Attacker controls: `assetId`, `routeConfig` (`createOmniBridgeRoute()` with no chain), `destinationAddress`
- Exploit idea: `OmniBridge.supports` requires a valid omni token or migrated PoA token, throws otherwise. Token specifics: PoA-named token MIGRATED to Omni via `POA_TOKENS_MIGRATED_TO_OMNI_BRIDGE` (ChainKind.Zcash, UTXO chain).
- Invariant to test: The bridge contract and chain named by the produced intent must equal the custodian of `nep141:zec.omft.near` and the chain the caller named; a mismatch must throw, never fall through to the next bridge.
- Expected Immunefi impact: Critical - funds delivered to a wrong address/chain/contract with no recovery (HackenProof: cross-chain address validation / withdrawal processing; Immunefi class: direct theft or permanent loss of user funds)
- Fast validation: vitest: construct IntentsSDK with mocked RPC/HTTP, call `IntentsSDK.processWithdrawal` with `nep141:zec.omft.near` and `createOmniBridgeRoute()` with no chain, assert `bridge.route` and the intent's `receiver_id`/`recipient`/chain.
