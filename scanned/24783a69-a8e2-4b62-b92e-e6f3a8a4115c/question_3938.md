# Q3938: Emporium signature coverage: reuse a signed stack whose deadline is f [when amountChanges[i] is exact]

## Question
Can an unprivileged attacker reuse a signed stack whose deadline is far future across many victims' flows, where the replay guard is per-message not per-signer-nonce, to move a wallet owner's assets or fees to a destination or under terms the owner's EIP-712 signature never authorised, specifically when amountChanges[i] is exactly zero for the affected token (where the zero branch skips value movement)?

## Target
- File/function: contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol :: verifyWallet / runAction / cancelEmporiumMessage
- Entrypoint: Hinkal.transact (Emporium action)
- Attacker controls: EmporiumStack (ops, sig, maxFee, deadline), circomData.feeStructure/relay, emporiumMessage
- Exploit idea: execute under a CircomData the signer never bound, or grief the replay guard
- Invariant to test: (assets leaving the wallet, their destination) == (ops, maxFee) the owner signed
- Expected Immunefi impact: High: moving assets/executing calls a prover or wallet owner never authorised
- Fast validation: Foundry: sign a stack, execute it under a different CircomData, assert unauthorised movement
