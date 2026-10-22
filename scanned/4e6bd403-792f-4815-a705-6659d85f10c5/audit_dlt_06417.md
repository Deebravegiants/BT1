# [H] Protocol fees collected in PairFees are lost due to accrued yield

## Summary
Severity: High
Chain: Smart contract
Component: Fenix-Finance
Published: 2024-02-27
Source: https://github.com/hats-finance/Fenix-Finance-0x83dbe5aa378f3ce160ed084daf85f621289fb92f/issues/36
Type: hats-finding

## Details
**Github username:** --
**Twitter username:** yixxas
**Submission hash (on-chain):** 0xae1f76b5a32d3e0351aa083da118a068f0119b47c0927f634bc829d9b6526fbc
**Severity:** high

**Description:**
**Description**\
Fenix dexV2.sol functions like the typical dex, and support stable and non stable pairs. Rebasing ERC20 tokens such as USDB and WETH are supported. We can verify this by seeing that `Pair.sol` inherits `BlastERC20RebasingManage` so that yield for these rebasing token on Blast can be set.



Protocol fees collected are collected in terms of both `token0` and `token1` in `_update0` and `_update1`. These fees are sent to the PairFees contract. `claimFees()` can only claim up to the maximum amount as accounted for in the `claimable0[]` and `claimable1[]` array. It cannot claim any excess fees that were generated due to Blast yield. Fees due to WETH and USDB rebasing up will be lost forever.

**Recommended mitigation**\
PairFees should inherit `BlastERC20RebasingManage` as well so that it can set ERC20 yield mode to CLAIMABLE. Note that the default yield mode is AUTOMATIC.

**Attachments**

1. **Proof of Concept (PoC) File**
<!-- You must provide a file containing a proof of concept (PoC) that demonstrates the vulnerability you have discovered. -->

2. **Revised Code File (Optional)**
<!-- If possible, please provide a second file containing the revised code that offers a potential fix for the vulnerability. This file should include the following information:
- Comment with a clear explanation of the proposed fix.
- The revised code with your suggested changes.
- Any additional comments or explanations that clarify how the fix addresses the vulnerability. -->
