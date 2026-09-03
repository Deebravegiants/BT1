# Q5638: Emporium signature coverage: execute the signed ops under a CircomDat [when the tree has exactly one ]

## Question
Can an unprivileged attacker execute the signed ops under a CircomData whose feeStructure/relay the signer never saw, where verifyWallet covers only (emporiumMessage, ops, maxFee, deadline), to move a wallet owner's assets or fees to a destination or under terms the owner's EIP-712 signature never authorised, specifically when the tree has exactly one prior leaf (where roots[MINIMUM_INDEX] equals that leaf directly)?

## Target
- File/function: contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol :: verifyWallet / runAction / cancelEmporiumMessage
- Entrypoint: Hinkal.transact (Emporium action)
- Attacker controls: EmporiumStack (ops, sig, maxFee, deadline), circomData.feeStructure/relay, emporiumMessage
- Exploit idea: execute under a CircomData the signer never bound, or grief the replay guard
- Invariant to test: (assets leaving the wallet, their destination) == (ops, maxFee) the owner signed
- Expected Immunefi impact: High: moving assets/executing calls a prover or wallet owner never authorised
- Fast validation: Foundry: sign a stack, execute it under a different CircomData, assert unauthorised movement
