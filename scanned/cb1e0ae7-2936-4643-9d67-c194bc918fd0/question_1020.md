# Q1020: HinkalWrapper fee/forward mismatch: amounts[i]==0 or token==address(0) entri [under a token with 6 decimals]

## Question
Can an unprivileged attacker call HinkalWrapper.prooflessDeposit with amounts[i]==0 or token==address(0) entries skipped by the pull loop but forwarded to Hinkal, so the ETH/tokens forwarded to Hinkal (ethForHinkal / approvals) diverge from what the caller actually paid, letting them mint leaves or drain the wrapper's residual balance, specifically under a token with 6 decimals (where decimal scaling shifts the accounting boundary)?

## Target
- File/function: contracts/HinkalWrapper.sol :: prooflessDeposit / _settleFee / _pullAndApproveDepositTokens
- Entrypoint: HinkalWrapper.prooflessDeposit
- Attacker controls: feeStructure, erc20Addresses, amounts, msg.value
- Exploit idea: make forwarded value or approvals exceed pulled value
- Invariant to test: value forwarded to Hinkal + fee paid == value pulled from msg.sender + msg.value
- Expected Immunefi impact: Critical: direct theft of shielded or in-flight user funds
- Fast validation: Foundry: run with mismatched fee/deposit, assert wrapper residual or over-mint
