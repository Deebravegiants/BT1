# [H] fundAppeal function may revert permanently if appeal cost decreases

## Summary
Severity: High
Chain: Smart contract
Component: Cross-chain-Realitio-Proxy
Published: 2025-09-23
Source: https://github.com/hats-finance/Cross-chain-Realitio-Proxy-0x9efc47be23fb612aff9bce511bad4a308f1f4f39/issues/9
Type: hats-finding

## Details
**Github username:** --
  **Twitter username:** --
  **HATS Profile:** [HATS Profile](https://app.hats.finance/profile/AresAudits)

  **Beneficiary:** 0xC03e799bBd6E450ab88bFB5975Eb918c80A53b81
  **Submission hash (on-chain):** 0x606d15d194c3f3f18e14bc451e11f5e4f2f208ccf1ad20adad28acc06decc735
  **Severity:** high
  
  **Description:**
  **Description**\
Here A mid-round decrease in the arbitrator's appeal cost can cause an underflow in a calculation within the fundAppeal function, leading to a permanent revert that blocks the appeal process for a dispute.

**Attack Scenario**\
The fundAppeal() function in RealitioForeignProxyArbitrum.sol  calculates the remaining amount needed to fully fund an answer. It does this by fetching the current appealCost from the arbitrator and then subtracting the fees already paid for that round.
```solidity
// ... existing code ...
        uint256 appealCost = arbitrator.appealCost(disputeID, arbitratorExtraData);
        uint256 totalCost = appealCost + ((appealCost * multiplier) / MULTIPLIER_DIVISOR);

        // Take up to the amount necessary to fund the current round at the current costs.
        uint256 contribution = totalCost - (round.paidFees[_answer]) > msg.value
            ? msg.value
            : totalCost - (round.paidFees[_answer]);
// ... existing code ...
```

and here if the arbitrator.appealCost decreases after some funds have already been contributed, the new totalCost can be less than the amount already collected in round.paidFees[_answer]. When the code attempts to calculate totalCost - (round.paidFees[_answer]), the operation underflows and causes the transaction to revert. Because this state is not corrected, every subsequent attempt to fund that answer will also revert.


here the primary impact is a permanent DOS on the appeal mechanism for a dispute. Once an answer's funding enters this state, no more funds can be added, preventing the creation of an appeal. This stalls the dispute resolution process indefinitely for that question and can lock the fees contributed during that specific round, as they cannot be used to further the appeal.

**Attachments**

1. **Proof of Concept (PoC) File**
working on poc,will submit in comments when it is ready

2. **Revised Code File (Optional)**
<!-- If possible, please provide a second file containing the revised code that offers a potential fix for the vulnerability. This file should include the following information:

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Cross-chain-Realitio-Proxy-0x9efc47be23fb612aff9bce511bad4a308f1f4f39/issues/9_
