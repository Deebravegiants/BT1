# [H] The `LiquidityPool::requestWithdraw()` function is vulnerable to unchecked transfers, as it lacks verification of the return value in the external transferFrom call involving eETH.

## Summary
Severity: High
Chain: Smart contract
Component: ether-fi
Published: 2023-11-10
Source: https://github.com/hats-finance/ether-fi-0x36c3b77853dec9c4a237a692623293223d4b9bc4/issues/43
Type: hats-finding

## Details
**Github username:** @dappconsulting
**Twitter username:** 0xSCSamurai
**Submission hash (on-chain):** 0xaafb0409fd4bb808a559e0d6b4883f51d98cdaff1b5f04eb22c66ba772362072
**Severity:** high

**Description:**
**Description**\

The `LiquidityPool::requestWithdraw()` function is vulnerable to unchecked transfers, as it lacks verification of the return value in the external transferFrom call involving eETH.

If the transfer silently fails for whatever reason, i.e. if no `eETH` is transferred from the `msg.sender` account, the function call won't revert, instead it will just return `false`, but the user will now get a free NFT that represents his withdraw request.

Result: user withdraws free tokens/funds, and protocol internal accounting is messed up.

**Attack Scenario**\
- Innocent user can become lucky.
- clever malicious user/attacker can craft his `transferFrom()` transaction in such a way that it maximizes silent failure, which will increase the chances of getting free token funds...

**Attachments**

1. **Proof of Concept (PoC) File**
<!-- You must provide a file containing a proof of concept (PoC) that demonstrates the vulnerability you have discovered. -->

2. **Revised Code File (Optional)**
: Recommendation attached.
  
**Files:**
  - 0_HIGH_LiquidityPool::requestWithdraw.sol (https://hats-backend-prod.herokuapp.com/v1/files/QmeBqpsXQ87opqatLVeph6XSM3f38Lgd5eLHR19zLbHF6Z)
