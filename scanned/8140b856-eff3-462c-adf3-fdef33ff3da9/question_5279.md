# Q5279: HinkalWrapper fee/forward mismatch: feeRecipient set to a contract that re-e [when the external action is Em]

## Question
Can an unprivileged attacker call HinkalWrapper.prooflessDeposit with feeRecipient set to a contract that re-enters HinkalWrapper before the forward, so the ETH/tokens forwarded to Hinkal (ethForHinkal / approvals) diverge from what the caller actually paid, letting them mint leaves or drain the wrapper's residual balance, specifically when the external action is Emporium with signerAddress zero (where the unsigned stateless op path runs)?

## Target
- File/function: contracts/HinkalWrapper.sol :: prooflessDeposit / _settleFee / _pullAndApproveDepositTokens
- Entrypoint: HinkalWrapper.prooflessDeposit
- Attacker controls: feeStructure, erc20Addresses, amounts, msg.value
- Exploit idea: make forwarded value or approvals exceed pulled value
- Invariant to test: value forwarded to Hinkal + fee paid == value pulled from msg.sender + msg.value
- Expected Immunefi impact: Critical: direct theft of shielded or in-flight user funds
- Fast validation: Foundry: run with mismatched fee/deposit, assert wrapper residual or over-mint
