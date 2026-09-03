# Q5188: Emporium signature coverage: execute the signed ops under a CircomDat [when the external action is Em]

## Question
Can an unprivileged attacker execute the signed ops under a CircomData whose feeStructure/relay the signer never saw, where verifyWallet covers only (emporiumMessage, ops, maxFee, deadline), to move a wallet owner's assets or fees to a destination or under terms the owner's EIP-712 signature never authorised, specifically when the external action is Emporium with signerAddress zero (where the unsigned stateless op path runs)?

## Target
- File/function: contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol :: verifyWallet / runAction / cancelEmporiumMessage
- Entrypoint: Hinkal.transact (Emporium action)
- Attacker controls: EmporiumStack (ops, sig, maxFee, deadline), circomData.feeStructure/relay, emporiumMessage
- Exploit idea: execute under a CircomData the signer never bound, or grief the replay guard
- Invariant to test: (assets leaving the wallet, their destination) == (ops, maxFee) the owner signed
- Expected Immunefi impact: High: moving assets/executing calls a prover or wallet owner never authorised
- Fast validation: Foundry: sign a stack, execute it under a different CircomData, assert unauthorised movement
