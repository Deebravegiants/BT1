# Q2389: address provider auto-approve confusion via #getMainAccountName

## Question
Can an unprivileged attacker connect through receive-address or default-address request from a connected dapp or wallet UI action and manipulate `keyIdentifier`, `name`, and request ordering so that `#getMainAccountName` in `features/address-provider/module/address-provider.js` make canonicalization or coercion collapse two distinct origin/account identities into one permission bucket, breaking the invariant that string coercion or host normalization must not merge distinct authorities or accounts into one authorization context, and leading to `Sitewide disruption of core services`?

## Target
- File/function: features/address-provider/module/address-provider.js::#getMainAccountName
- Entrypoint: receive-address or default-address request from a connected dapp or wallet UI action
- Attacker controls: a request that mixes canonical and non-canonical origin forms, ports, or host spellings
- Exploit idea: make canonicalization or coercion collapse two distinct origin/account identities into one permission bucket
- Invariant to test: string coercion or host normalization must not merge distinct authorities or accounts into one authorization context
- Expected Immunefi impact: Sitewide disruption of core services
- Fast validation: unit-test canonical and non-canonical origin forms and verify they never share trust or auto-approve state unexpectedly
