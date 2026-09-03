# Q0688: Emporium signature coverage: execute the signed ops under a CircomDat [when a prior tx in the same bl]

## Question
Can an unprivileged attacker execute the signed ops under a CircomData whose feeStructure/relay the signer never saw, where verifyWallet covers only (emporiumMessage, ops, maxFee, deadline), to move a wallet owner's assets or fees to a destination or under terms the owner's EIP-712 signature never authorised, specifically when a prior tx in the same block left the action or tree in a partial state (where cross-tx residual state carries over)?

## Target
- File/function: contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol :: verifyWallet / runAction / cancelEmporiumMessage
- Entrypoint: Hinkal.transact (Emporium action)
- Attacker controls: EmporiumStack (ops, sig, maxFee, deadline), circomData.feeStructure/relay, emporiumMessage
- Exploit idea: execute under a CircomData the signer never bound, or grief the replay guard
- Invariant to test: (assets leaving the wallet, their destination) == (ops, maxFee) the owner signed
- Expected Immunefi impact: High: moving assets/executing calls a prover or wallet owner never authorised
- Fast validation: Foundry: sign a stack, execute it under a different CircomData, assert unauthorised movement
