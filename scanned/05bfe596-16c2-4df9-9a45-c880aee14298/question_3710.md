# Q3710: Plasma token-address block bypass via HotBridge (a malformed token-addres)

## Question
On the HotBridge route for Plasma, can an unprivileged user pass `destinationAddress` equal to a malformed token-address string that makes `compareAddresses` throw internally and return false so that `compareAddresses(tokenAddress, destinationAddress, 'eip155:9745')` returns false, `DestinationAddressMatchesTokenAddressError` is not thrown, and the withdrawal sends tokens to the token contract itself where they are unrecoverable?

## Target
- File/function: packages/intents-sdk/src/lib/compareAddresses.ts `compareAddresses`; packages/intents-sdk/src/bridges/hot-bridge/hot-bridge.ts `validateWithdrawal`
- Entrypoint: `IntentsSDK.processWithdrawal` / `createWithdrawalIntents`
- Attacker controls: `destinationAddress` (a malformed token-address string that makes `compareAddresses` throw internally and return false) for a Plasma asset
- Exploit idea: `compareAddresses` returns false on any thrown error and only canonicalises for EVM/hex/TON/Tron/Stellar; for Plasma it uses `getAddress`. `validateAddress` may accept a form `compareAddresses` cannot canonicalise.
- Invariant to test: For every accepted destination d and token address t on Plasma: if d and t denote the same account, `compareAddresses(t, d)` must be true.
- Expected Immunefi impact: Critical - funds delivered to a wrong address/chain/contract with no recovery (HackenProof: cross-chain address validation / withdrawal processing; Immunefi class: direct theft or permanent loss of user funds)
- Fast validation: vitest: enumerate encodings of a Plasma token address that pass `validateAddress`, assert `compareAddresses` is true for each.
