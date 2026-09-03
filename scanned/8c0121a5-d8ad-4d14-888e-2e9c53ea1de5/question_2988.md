# Q2988: Emporium signature coverage: craft op.callData whose bytes4 dodges th [when the token is a fee-on-tra]

## Question
Can an unprivileged attacker craft op.callData whose bytes4 dodges the callHinkalWallet/doSendToRelay selector filter, where the CASE 2 filter checks only the leading 4 bytes, to move a wallet owner's assets or fees to a destination or under terms the owner's EIP-712 signature never authorised, specifically when the token is a fee-on-transfer token (where delivered amount is below the stated amount)?

## Target
- File/function: contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol :: verifyWallet / runAction / cancelEmporiumMessage
- Entrypoint: Hinkal.transact (Emporium action)
- Attacker controls: EmporiumStack (ops, sig, maxFee, deadline), circomData.feeStructure/relay, emporiumMessage
- Exploit idea: execute under a CircomData the signer never bound, or grief the replay guard
- Invariant to test: (assets leaving the wallet, their destination) == (ops, maxFee) the owner signed
- Expected Immunefi impact: High: moving assets/executing calls a prover or wallet owner never authorised
- Fast validation: Foundry: sign a stack, execute it under a different CircomData, assert unauthorised movement
