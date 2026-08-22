# [M] Anyone can prevent liquidation by repaying as little as 1 wei

## Summary
Severity: Medium
Chain: Smart contract
Component: Ion-Protocol
Published: 2024-01-22
Source: https://github.com/hats-finance/Ion-Protocol-0x20c44e7b618d58f9982e28de66d8d6ee176eb481/issues/20
Type: hats-finding

## Details
**Github username:** --
**Twitter username:** kodyvim_
**Submission hash (on-chain):** 0xff63cab0c24ea7af38bc919b8dbe2b0292dd3515dd7239495689af0c987b834e
**Severity:** medium

**Description:**
**Description**\
Attacker can prevent liquidation with as little as 1 wei
**Attack Scenario**\
An attacker can frontrun call to `liquidate` with repaydebt of at least 1 wei to prevent legit liquidations, this would result to accumulation of bad debt.
Attacker can repeat this to make the liquidation of profitable or expensive.

**Attachments**

1. **Proof of Concept (PoC) File**
```solidity
function repayBadDebt(address user, uint256 rad) external whenNotPaused {
        IonPoolStorage storage $ = _getIonPoolStorage();

        $.unbackedDebt[user] -= rad;
        $.totalUnbackedDebt -= rad;
        $.debt -= rad;

        // Must be negative since it is a repayment
        _transferWeth(_msgSender(), -(rad.toInt256()));

        emit RepayBadDebt(user, _msgSender(), rad);
    }
```

```solidity
// pay off the unbacked debt
        POOL.repayBadDebt(address(this), liquidateArgs.repay);
```

2. **Revised Code File (Optional)**
<!-- If possible, please provide a second file containing the revised code that offers a potential fix for the vulnerability. This file should include the following information:
- Comment with a clear explanation of the proposed fix.

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Ion-Protocol-0x20c44e7b618d58f9982e28de66d8d6ee176eb481/issues/20_
