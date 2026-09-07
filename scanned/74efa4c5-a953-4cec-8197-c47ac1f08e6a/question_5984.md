# Q5984: Dash token-address block bypass via PoaBridge (a different textual enco)

## Question
On the PoaBridge route for Dash, can an unprivileged user pass `destinationAddress` equal to a different textual encoding of the bridged token's own contract address so that `compareAddresses(tokenAddress, destinationAddress, 'bip122:00000ffd590b1485b3caadc19b22e637')` returns false, `DestinationAddressMatchesTokenAddressError` is not thrown, and the withdrawal sends tokens to the token contract itself where they are unrecoverable?

## Target
- File/function: packages/intents-sdk/src/lib/compareAddresses.ts `compareAddresses`; packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts `validateWithdrawal`
- Entrypoint: `IntentsSDK.processWithdrawal` / `createWithdrawalIntents`
- Attacker controls: `destinationAddress` (a different textual encoding of the bridged token's own contract address) for a Dash asset
- Exploit idea: `compareAddresses` returns false on any thrown error and only canonicalises for EVM/hex/TON/Tron/Stellar; for Dash it uses `raw string or chain-specific normaliser`. `validateAddress` may accept a form `compareAddresses` cannot canonicalise.
- Invariant to test: For every accepted destination d and token address t on Dash: if d and t denote the same account, `compareAddresses(t, d)` must be true.
- Expected Immunefi impact: Critical - funds delivered to a wrong address/chain/contract with no recovery (HackenProof: cross-chain address validation / withdrawal processing; Immunefi class: direct theft or permanent loss of user funds)
- Fast validation: vitest: enumerate encodings of a Dash token address that pass `validateAddress`, assert `compareAddresses` is true for each.
