# [M] Lack of Function for Receiving ETH

## Summary
Severity: Medium
Chain: Smart contract
Component: Possum-Labs--Portals-
Published: 2023-11-21
Source: https://github.com/hats-finance/Possum-Labs--Portals--0xed8965d49b8aeca763447d56e6da7f4e0506b2d3/issues/69
Type: hats-finding

## Details
**Github username:** @0xmahdirostami
**Twitter username:** 0xmahdirostami
**Submission hash (on-chain):** 0x3b7af53203989533bd7c2df589e9a9bdfd222f2735e67c99b2958e752fdc2296
**Severity:** medium

**Description:**
**Description**\
As mentioned in issue #39, one of the edge cases is receiving yield as ETH. However, the current implementation doesn't have a function for receiving ETH. This means yield sources cannot send ETH to the contract, resulting in arbitrageurs not using the convert function and causing a direct loss of funds for funders.

**Impact**\
This vulnerability prevents the contract from efficiently receiving ETH as yield, impacting the overall functionality and potential losses for funders.


**Revised Code File (Optional)**\
```diff
+	receive() external payable { }
```
