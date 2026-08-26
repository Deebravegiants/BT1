# [M] Missing check of return value of transferFrom

## Summary
Severity: Medium
Chain: Smart contract
Component: Ion-Protocol
Published: 2024-02-05
Source: https://github.com/hats-finance/Ion-Protocol-0x20c44e7b618d58f9982e28de66d8d6ee176eb481/issues/50
Type: hats-finding

## Details
**Github username:** --
**Twitter username:** --
**Submission hash (on-chain):** 0xbf8701ccc779ab00b9500417674d12c09ff90519711a3e25dc452ffc592fba5f
**Severity:** medium

**Description:**
**Description**\
The return value of `transferFrom` calls is not being checked in many contracts. A call to transferFrom or transfer is frequently done without checking the results. For certain ERC20 tokens, if insufficient tokens are present, no revert occurs but a result of "false" is returned. So its important to check this. If you don't you could mint tokens without have received sufficient tokens to do so. So you could loose funds.

Its also a best practice to check this. See below for example where the result isn't checked.


**Attachments**
    1. Function: `zapDepositAndBorrow(uint256,uint256,bytes32[])`
Location: `WstEthHandler.sol` Lines #69-80
Observation: The return value of `STETH.transferFrom(msg.sender, address(this), stEthAmount)` at line #77 is not being checked.

2. Function: `zapFlashLeverageCollateral(uint256,uint256,uint256,bytes32[])`
Location: `WstEthHandler.sol` Lines #82-99
Observation: The return value of `STETH.transferFrom(msg.sender, address(this), initialDeposit)` at line #92 is not being checked.

3. Function: `zapFlashLeverageWeth(uint256,uint256,uint256,bytes32[])`
Location: `WstEthHandler.sol` Lines #101-118
Observation: The return value of `STETH.transferFrom(msg.sender, address(this), initialDeposit)` at line #111 is not being checked.

4. Function: `zapFlashswapLeverage(uint256,uint256,uint256,uint160,uint256,bytes32[])`
Location: `WstEthHandler.sol` Lines #120-143
Observation: The return value of `STETH.transferFrom(msg.sender, address(this), initialDeposit)` at line #133 is not being checked.


1. **Proof of Concept (PoC) File**

2. **Revised Code File (Optional)**
<!-- If possible, please provide a second file containing the revised code that offers a potential fix for the vulnerability. This file should include the following information:
- Comment with a clear explanation of the proposed fix.
- The revised code with your suggested changes.
- Any additional comments or explanations that clarify how the fix addresses the vulnerability. -->
