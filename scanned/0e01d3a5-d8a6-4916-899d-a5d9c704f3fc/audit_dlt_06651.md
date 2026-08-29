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


_Trimmed to 38 lines — full report: https://github.com/hats-finance/DAOsis-0x8ef21ecb2af12ce9cc0e475eec25f90a9622b4f4/issues/142_
