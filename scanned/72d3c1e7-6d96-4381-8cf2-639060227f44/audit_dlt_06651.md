# [H] `invest()` Function Allows Investments Even After Sale Has Ended

## Summary
Severity: High
Chain: Smart contract
Component: DAOsis
Published: 2025-02-08
Source: https://github.com/hats-finance/DAOsis-0x8ef21ecb2af12ce9cc0e475eec25f90a9622b4f4/issues/142
Type: hats-finding

## Details
**Github username:** --
  **Twitter username:** --
  **HATS Profile:** [HATS Profile](https://app.hats.finance/profile/AresAudits)

  **Beneficiary:** 0xC03e799bBd6E450ab88bFB5975Eb918c80A53b81
  **Submission hash (on-chain):** 0x74a403e08f4216f7bb53a6e242e627ce2699abfa2667dc7d2bf63fbe5f10308d
  **Severity:** high
  
  **Description:**
  **Description**\
below is the `invest()` function in exchange.sol smart contract

```solidity
function invest(uint256 amount, address _investor) external whenNotPaused onlyOwner {//@audit - no endTime check
        require((totalRaisedUSD + amount) <= targetUSD,"Max Cap Reached");
        uint256 tokenAmount = (amount / tokenPrice) * 1e18;
        investments[_investor] += amount;
        tokensToReceive[_investor] += tokenAmount;
        totalRaisedUSD += amount;
        totalTokensSold += tokenAmount;
        investors.push(_investor);

        emit InvestmentReceived(_investor, amount, tokenAmount);
    }
```

here this function allows owner to process investments and allocates tokens to investors.However, **it does not include a check to ensure that investments are only accepted before the `endTime` of the sale**.
This oversight allows investments to be made **even after the sale has officially ended**, which can lead to inconsistencies and potential disputes


**Attack Scenario**\
lets understand this with example

**Initial Setup:**

* The sale has an `endTime` set to a specific timestamp, indicating when the sale should conclude.
* The current time (block.timestamp) is beyond this `endTime` i.e block.timestamp > endTime

**Issue:**
* The function processes the investment without checking if the current time is past the endTime.
* This results in the acceptance of investments beyond the intended sale period.

**Attachments**

1. **Proof of Concept (PoC) File**
<!-- You must provide a file containing a proof of concept (PoC) that demonstrates the vulnerability you have discovered. -->
```solidity
function invest(uint256 amount, address _investor) external whenNotPaused onlyOwner {//@audit - no endTime check
        require((totalRaisedUSD + amount) <= targetUSD,"Max Cap Reached");
        uint256 tokenAmount = (amount / tokenPrice) * 1e18;
        investments[_investor] += amount;
        tokensToReceive[_investor] += tokenAmount;
        totalRaisedUSD += amount;
        totalTokensSold += tokenAmount;
        investors.push(_investor);

        emit InvestmentReceived(_investor, amount, tokenAmount);
    }
```

2. **Revised Code File (Optional)**
<!-- If possible, please provide a second file containing the revised code that offers a potential fix for the vulnerability. This file should include the following information:
- Comment with a clear explanation of the proposed fix.
- The revised code with your suggested changes.
- Any additional comments or explanations that clarify how the fix addresses the vulnerability. -->
```solidity
   // Revised invest function with validation for endTime
   function invest(uint256 amount, address _investor) external whenNotPaused onlyOwner {
       require(block.timestamp <= endTime, "Sale has ended"); // Added validation for endTime
       require((totalRaisedUSD + amount) <= targetUSD, "Max Cap Reached");
       uint256 tokenAmount = (amount * 1e18) / tokenPrice; // Corrected token amount calculation
       investments[_investor] += amount;
       tokensToReceive[_investor] += tokenAmount;
       totalRaisedUSD += amount;
       totalTokensSold += tokenAmount;
       investors.push(_investor);

       emit InvestmentReceived(_investor, amount, tokenAmount);
   }
```
* this code introduces a validation check to ensure that investments are only accepted if the current time is before the endTime
