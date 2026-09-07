# Q0509: Zcash token-address block bypass via OmniBridge (a malformed token-addres)

## Question
On the OmniBridge route for Zcash, can an unprivileged user pass `destinationAddress` equal to a malformed token-address string that makes `compareAddresses` throw internally and return false so that `compareAddresses(tokenAddress, destinationAddress, 'bip122:00040fe8ec8471911baa1db1266ea15d')` returns false, `DestinationAddressMatchesTokenAddressError` is not thrown, and the withdrawal sends tokens to the token contract itself where they are unrecoverable?

## Target
- File/function: packages/intents-sdk/src/lib/compareAddresses.ts `compareAddresses`; packages/intents-sdk/src/bridges/omni-bridge/omni-bridge.ts `validateWithdrawal`
- Entrypoint: `IntentsSDK.processWithdrawal` / `createWithdrawalIntents`
- Attacker controls: `destinationAddress` (a malformed token-address string that makes `compareAddresses` throw internally and return false) for a Zcash asset
- Exploit idea: `compareAddresses` returns false on any thrown error and only canonicalises for EVM/hex/TON/Tron/Stellar; for Zcash it uses `raw string or chain-specific normaliser`. `validateAddress` may accept a form `compareAddresses` cannot canonicalise.
- Invariant to test: For every accepted destination d and token address t on Zcash: if d and t denote the same account, `compareAddresses(t, d)` must be true.
- Expected Immunefi impact: Critical - funds delivered to a wrong address/chain/contract with no recovery (HackenProof: cross-chain address validation / withdrawal processing; Immunefi class: direct theft or permanent loss of user funds)
- Fast validation: vitest: enumerate encodings of a Zcash token address that pass `validateAddress`, assert `compareAddresses` is true for each.
