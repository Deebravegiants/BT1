# Q3951: Abstract token-address block bypass via OmniBridge (a different textual enco)

## Question
On the OmniBridge route for Abstract, can an unprivileged user pass `destinationAddress` equal to a different textual encoding of the bridged token's own contract address so that `compareAddresses(tokenAddress, destinationAddress, 'eip155:2741')` returns false, `DestinationAddressMatchesTokenAddressError` is not thrown, and the withdrawal sends tokens to the token contract itself where they are unrecoverable?

## Target
- File/function: packages/intents-sdk/src/lib/compareAddresses.ts `compareAddresses`; packages/intents-sdk/src/bridges/omni-bridge/omni-bridge.ts `validateWithdrawal`
- Entrypoint: `IntentsSDK.processWithdrawal` / `createWithdrawalIntents`
- Attacker controls: `destinationAddress` (a different textual encoding of the bridged token's own contract address) for a Abstract asset
- Exploit idea: `compareAddresses` returns false on any thrown error and only canonicalises for EVM/hex/TON/Tron/Stellar; for Abstract it uses `getAddress`. `validateAddress` may accept a form `compareAddresses` cannot canonicalise.
- Invariant to test: For every accepted destination d and token address t on Abstract: if d and t denote the same account, `compareAddresses(t, d)` must be true.
- Expected Immunefi impact: Critical - funds delivered to a wrong address/chain/contract with no recovery (HackenProof: cross-chain address validation / withdrawal processing; Immunefi class: direct theft or permanent loss of user funds)
- Fast validation: vitest: enumerate encodings of a Abstract token address that pass `validateAddress`, assert `compareAddresses` is true for each.
