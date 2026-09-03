# Q4402: Emporium signature coverage: make feeStructure.flatFee <= maxFee but  [when the feeStructure.feeToken]

## Question
Can an unprivileged attacker make feeStructure.flatFee <= maxFee but relay routing sends fees to an attacker relay, where fee destination is not part of the signed payload, to move a wallet owner's assets or fees to a destination or under terms the owner's EIP-712 signature never authorised, specifically when the feeStructure.feeToken equals the affected token (where flat/variable fee deduction overlaps the leg)?

## Target
- File/function: contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol :: verifyWallet / runAction / cancelEmporiumMessage
- Entrypoint: Hinkal.transact (Emporium action)
- Attacker controls: EmporiumStack (ops, sig, maxFee, deadline), circomData.feeStructure/relay, emporiumMessage
- Exploit idea: execute under a CircomData the signer never bound, or grief the replay guard
- Invariant to test: (assets leaving the wallet, their destination) == (ops, maxFee) the owner signed
- Expected Immunefi impact: High: moving assets/executing calls a prover or wallet owner never authorised
- Fast validation: Foundry: sign a stack, execute it under a different CircomData, assert unauthorised movement
