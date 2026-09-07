# Q1754: Omni override nep141:base-0x833589fcd6ed -> Solana

## Question
Using `createOmniBridgeRoute(Chains.Solana)` for `nep141:base-0x833589fcd6edb6e08f4c7c32d4f71b54bda02913.omft.near` (origin Base), `OmniBridge.supports` skips `validateOmniToken`/`parseOriginChain` because `targetChainSpecified` is true and only requires `getBridgedToken(nep141, ChainKind.Solana)` != null. Can an unprivileged caller thereby withdraw to Solana where the bridged representation is a different asset (different decimals or a wrapper the user cannot redeem), or where `compareAddresses`/`validateAddress` run for Solana while the token's own origin address rules differ, so the received value differs from the signed amount?

## Target
- File/function: packages/intents-sdk/src/bridges/omni-bridge/omni-bridge.ts `supports`, `makeAssetInfo`, `validateWithdrawal` (decimals via `getCachedTokenDecimals`), `createWithdrawalIntents`; omni-withdraw-params.ts `caip2ToChainKind`
- Entrypoint: `IntentsSDK.processWithdrawal` with `createOmniBridgeRoute(chain)`
- Attacker controls: `routeConfig.chain` = Solana, `assetId` = `nep141:base-0x833589fcd6edb6e08f4c7c32d4f71b54bda02913.omft.near`, `destinationAddress` on Solana
- Exploit idea: Chain override path trusts the caller's chain and the existence of a bridged token address; it never checks the token is meant to be withdrawn there or that decimals normalisation preserves value.
- Invariant to test: amount credited on Solana (after `verifyTransferAmount` normalisation) == signed amount - fees, in the same asset the user holds.
- Expected Immunefi impact: Critical - funds delivered to a wrong address/chain/contract with no recovery (HackenProof: cross-chain address validation / withdrawal processing; Immunefi class: direct theft or permanent loss of user funds)
- Fast validation: vitest: mock `getBridgedToken` returning an address and `getTokenDecimals` with mismatched decimals; assert intents and min-amount checks.
