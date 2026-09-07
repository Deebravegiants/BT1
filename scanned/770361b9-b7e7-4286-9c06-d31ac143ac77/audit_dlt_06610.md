# [M] depositWithSignature() function can be affected by DOS

## Summary
Severity: Medium
Chain: Smart contract
Component: Accumulated-finance
Published: 2024-09-09
Source: https://github.com/hats-finance/Accumulated-finance-0x75278bcc0fa7c9e3af98654bce195eaf3bb6a784/issues/63
Type: hats-finding

## Details
**Github username:** @0xRizwan
**Twitter username:** 0xRizwann
**Submission hash (on-chain):** 0x65db4f9773c0e4f7ecce60decd9cb1711a85e625ffec2b6bf429a25b1954497d
**Severity:** medium

**Description:**
### Title
`depositWithSignature(()` function can be affected by DOS

### Severity
Medium

### Affected contracts
wrstMTRG.sol, wstARB.sol, wstDOJ.sol, wstMANTA.sol, wstMETIS.sol, wstROSE.sol, wstVLX.sol, wstZETA.sol and wstToken.sol

### Vulnerability Detail
In `wstToken.sol` `depositWithSignature(()` function is used to deposit the assets via permit in single transaction. 

```solidity
    function depositWithSignature(
        uint256 assets,
        address receiver,
        uint256 deadline,
        bool approveMax,
        uint8 v,
        bytes32 r,
        bytes32 s
    ) external nonReentrant returns (uint256 shares) {
        uint256 amount = approveMax ? type(uint256).max : assets;
@>        asset.permit(msg.sender, address(this), amount, deadline, v, r, s);
        return (deposit(assets, receiver));
    }
```
The issue is that while the transactions for depositWithSignature() function is in mempool, anyone could extract the signature parameters from the call to front-run the transaction with direct permit call.

This issue is originally submitted by Trust security aka Trust to various on chain protocols and the issue is confirmed by reputed protocols like Open Zeppelin, AAVE, The Graph, Uniswap-V2.

To understand the issue in detail, Please refer below link:

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Accumulated-finance-0x75278bcc0fa7c9e3af98654bce195eaf3bb6a784/issues/63_
