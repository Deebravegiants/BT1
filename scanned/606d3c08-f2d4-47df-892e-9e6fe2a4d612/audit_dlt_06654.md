# [M] updateEndTime Function Allows Setting Invalid Timestamps and sale can be extend indefinitely

## Summary
Severity: Medium
Chain: Smart contract
Component: DAOsis
Published: 2025-02-08
Source: https://github.com/hats-finance/DAOsis-0x8ef21ecb2af12ce9cc0e475eec25f90a9622b4f4/issues/139
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

```solidity
function updateEndTime(uint256 _endTime) external onlyOwner {//@audit - multiple critical checks missing
        endTime = _endTime;
    }
```
the above function allows `owner` to to modify the `endTime` of the token sale without any validation checks.critical checks missing for below cases 

* The function allows updates to the endTime even after the sale has ended.

* There is no validation to ensure the new endTime is after the startTime.

* The function can set the endTime to a past timestamp, potentially ending the sale immediately

* There is no event emission for this critical state change

**Attack Scenario**\
N/A

**Attachments**

1. **Proof of Concept (PoC) File**
below is the vulnerable function :

```solidity

function updateEndTime(uint256 _endTime) external onlyOwner {//@audit- multiple critical checks missing
        endTime = _endTime;
```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/DAOsis-0x8ef21ecb2af12ce9cc0e475eec25f90a9622b4f4/issues/139_
