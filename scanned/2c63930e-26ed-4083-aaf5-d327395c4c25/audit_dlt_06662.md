# [M] Unupdated MaxCap After Token Burn Creates State Inconsistency

## Summary
Severity: Medium
Chain: Smart contract
Component: DAOsis
Published: 2025-01-29
Source: https://github.com/hats-finance/DAOsis-0x8ef21ecb2af12ce9cc0e475eec25f90a9622b4f4/issues/91
Type: hats-finding

## Details
**Github username:** --
  **Twitter username:** --
  **HATS Profile:** [HATS Profile](https://app.hats.finance/profile/0xvd)

  **Beneficiary:** 0x23B5FbcF9dc2C5d5D6fDCd36d2239E6fC3aED2BA
  **Submission hash (on-chain):** 0x6a938436f609f22f0c8ab9ef5c99272917366fbafd439c66c37427f146b52579
  **Severity:** medium
  
  **Description:**
  **Description**\
The FastTrackIDO contract's burnToken function burns unsold tokens after a failed IDO but fails to update the maxCap state variable to reflect the new total supply. 

This creates an inconsistency between the actual available tokens and the contract's state, potentially leading to incorrect calculations and allowing multiple burn operations.

The function burns tokens but maintains the original maxCap value:

```Solidity
function burnToken() external onlyOwner whenNotPaused {
        require(block.timestamp > endTime, "IDO has not ended yet");
        require(totalRaised < maxCap, "MaxCap was reached, no tokens to burn");

        ERC20Token token = ERC20Token(tokenAddress);
        //@audit incorrect handling of deciamls?
        uint256 unsoldTokens = ((maxCap - totalRaised) *
            10 ** token.decimals()) / tokenPrice;
        //@audit unnecessary require statement
        require(unsoldTokens > 0, "No unsold tokens to burn");
        //@audit reset max cap??
        token.burn(unsoldTokens);

        emit TokensBurned(msg.sender, unsoldTokens);
    }
```

**Attack Scenario**\

Consider an IDO with:


_Trimmed to 38 lines — full report: https://github.com/hats-finance/DAOsis-0x8ef21ecb2af12ce9cc0e475eec25f90a9622b4f4/issues/91_
