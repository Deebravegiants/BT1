# [H] The unstake function may cause the status update of global variables to be out of sync.

## Summary
Severity: High
Chain: Smart contract
Component: Possum-Labs--Portals-
Published: 2023-11-16
Source: https://github.com/hats-finance/Possum-Labs--Portals--0xed8965d49b8aeca763447d56e6da7f4e0506b2d3/issues/21
Type: hats-finding

## Details
**Github username:** --
**Twitter username:** --
**Submission hash (on-chain):** 0x19766be033a8eeade9f5a5347d9d38912c608c7875cdc76a4766ab30d8979e64
**Severity:** high

**Description:**
**Description**\
In `Portal.sol.` 
The attacker first stakes a token. Then call the unstake function multiple times, passing in a small amount parameter, which will make the updates between the four global variables `accounts[msg.sender].stakedBalance`, `accounts[msg.sender].maxStakeDebt`, `accounts[msg.sender].portalEnergy` and `accounts[msg. sender].availableToWithdraw` are not synchronized.

**Attack Scenario**\
First of all, the value of `maxLockDuration` is 7776000, and the value of `SECONDS_PER_YEAR` is 31536000. The value of the former is smaller than the latter. And `31536000 / 7776000 = 4.055555555555555`. This shows that if you `unstake` the tokens with amount of `4` each time, the values of the two global variables `accounts[msg.sender].stakedBalance` and `accounts[msg.sender].availableToWithdraw` will continue to become smaller, and The values of `accounts[msg.sender].maxStakeDebt` and `accounts[msg.sender].portalEnergy` remain unchanged. This vulnerability allows users to keep the values of `accounts[msg.sender].maxStakeDebt` and `accounts[msg.sender].portalEnergy` unchanged while unstaking all their own tokens.

**Attachments**

1. **Proof of Concept (PoC) File**
<!-- You must provide a file containing a proof of concept (PoC) that demonstrates the vulnerability you have discovered. -->

2. **Revised Code File (Optional)**
<!-- If possible, please provide a second file containing the revised code that offers a potential fix for the vulnerability. This file should include the following information:
- Comment with a clear explanation of the proposed fix.
- The revised code with your suggested changes.
- Any additional comments or explanations that clarify how the fix addresses the vulnerability. -->
