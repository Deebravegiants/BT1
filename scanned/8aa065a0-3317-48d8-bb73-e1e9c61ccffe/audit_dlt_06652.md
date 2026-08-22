# [H] `invest()` function does not check for Maximum Tokens Available for Sale

## Summary
Severity: High
Chain: Smart contract
Component: DAOsis
Published: 2025-02-08
Source: https://github.com/hats-finance/DAOsis-0x8ef21ecb2af12ce9cc0e475eec25f90a9622b4f4/issues/141
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
below is the `invest()` function,

exchange.sol::invest()

```solidity
function invest(uint256 amount, address _investor) external whenNotPaused onlyOwner {//@audit - no check for tokensForSale
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
here this function allows the `owner` to process investments and allocate tokens to investors.However, **it does not include a check to ensure that the total number of tokens sold does not exceed the tokensForSale limit**.This can leads to the sale of more tokens than intended.

**Attack Scenario**\
consider below example scenario

**Initial Setup:**
* tokensForSale is set to 10,000 tokens.
* totalTokensSold is currently 9,500 tokens.

**Investment Scenario:**
* An investor makes an investment that should result in the allocation of 1,000 tokens.

_Trimmed to 38 lines — full report: https://github.com/hats-finance/DAOsis-0x8ef21ecb2af12ce9cc0e475eec25f90a9622b4f4/issues/141_
