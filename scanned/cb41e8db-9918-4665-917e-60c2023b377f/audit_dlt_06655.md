# [M] Lack of Validation for endTime in startSale Function Allows Setting Past Timestamps

## Summary
Severity: Medium
Chain: Smart contract
Component: DAOsis
Published: 2025-02-08
Source: https://github.com/hats-finance/DAOsis-0x8ef21ecb2af12ce9cc0e475eec25f90a9622b4f4/issues/138
Type: hats-finding

## Details
**Github username:** --
  **Twitter username:** --
  **HATS Profile:** [HATS Profile](https://app.hats.finance/profile/AresAudits)

  **Beneficiary:** 0xC03e799bBd6E450ab88bFB5975Eb918c80A53b81
  **Submission hash (on-chain):** 0xfc3b99510d76ed406f41080f9cd9b6b58d5716feca73ba14da109ba79a8248fd
  **Severity:** medium
  
  **Description:**
  **Description**\
below is the startSale() function in exchange.sol smart contract

exchange.sol::startSale()

```solidity
 function startSale(uint256 _endTime) external onlyOwner {//@audit-no validation on endtime
        require(startTime == 0, "Sale Already Started");
        startTime = block.timestamp;
        endTime = _endTime;
    }
```
the above function allows the owner to set the `endTime` of the token sale. However, there is no validation to ensure that the **endTime is set to a future timestamp**. This oversight allows the **endTime to be set to a past timestamp**, which could immediately end the sale upon starting

**Attack Scenario**\
here  owner, either maliciously or accidentally, could set the `endTime` to a timestamp that is less than the current block.timestamp. This would mean the sale is considered ended as soon as it starts

**Attachments**

1. **Proof of Concept (PoC) File**
<!-- You must provide a file containing a proof of concept (PoC) that demonstrates the vulnerability you have discovered. -->
```solidity
function startSale(uint256 _endTime) external onlyOwner {//@audit- no input validation
        require(startTime == 0, "Sale Already Started");
        startTime = block.timestamp;
        endTime = _endTime;
    }
```
2. **Revised Code File (Optional)**

_Trimmed to 38 lines — full report: https://github.com/hats-finance/DAOsis-0x8ef21ecb2af12ce9cc0e475eec25f90a9622b4f4/issues/138_
