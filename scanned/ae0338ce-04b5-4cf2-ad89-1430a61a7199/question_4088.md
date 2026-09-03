# Q4088: Emporium signature coverage: front-run to set usedMessages[emporiumMe [when onChainCreation[i] is tru]

## Question
Can an unprivileged attacker front-run to set usedMessages[emporiumMessage] before the real signer, via cancelEmporiumMessage, where cancelEmporiumMessage accepts any signer recovering to msg.sender, to move a wallet owner's assets or fees to a destination or under terms the owner's EIP-712 signature never authorised, specifically when onChainCreation[i] is true for the affected token (where the RHS of the balance equation drops the amount term)?

## Target
- File/function: contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol :: verifyWallet / runAction / cancelEmporiumMessage
- Entrypoint: Hinkal.transact (Emporium action)
- Attacker controls: EmporiumStack (ops, sig, maxFee, deadline), circomData.feeStructure/relay, emporiumMessage
- Exploit idea: execute under a CircomData the signer never bound, or grief the replay guard
- Invariant to test: (assets leaving the wallet, their destination) == (ops, maxFee) the owner signed
- Expected Immunefi impact: High: moving assets/executing calls a prover or wallet owner never authorised
- Fast validation: Foundry: sign a stack, execute it under a different CircomData, assert unauthorised movement
