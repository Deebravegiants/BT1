# [M] depositWithSignature() won't work and always revert due to missing permit function in deposited asset

## Summary
Severity: Medium
Chain: Smart contract
Component: Accumulated-finance
Published: 2024-09-09
Source: https://github.com/hats-finance/Accumulated-finance-0x75278bcc0fa7c9e3af98654bce195eaf3bb6a784/issues/62
Type: hats-finding

## Details
**Github username:** @0xRizwan
**Twitter username:** 0xRizwann
**Submission hash (on-chain):** 0x65db4f9773c0e4f7ecce60decd9cb1711a85e625ffec2b6bf429a25b1954497d
**Severity:** medium

**Description:**
### Title
`depositWithSignature()` won't work and always revert due to missing permit function in deposited asset.

### Severity
Medium

### Affected contracts
`wrstMTRG.sol`, `wstARB.sol`, `wstDOJ.sol`, `wstMANTA.sol`, `wstMETIS.sol`, `wstROSE.sol`, `wstVLX.sol`, `wstZETA.sol` and `wstToken.sol`

### Vulnerability Detail
`wstToken.sol` is the referred contract from which the above contracts are deployed. wstToken is ERC4626 compatible. For example, in case of  `wstROSE.sol`, it allows to deposit `stROSE` token and mints `wstROSE` tokens. This issue is with `depositWithSignature()` function of `wstToken.sol`:

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
        asset.permit(msg.sender, address(this), amount, deadline, v, r, s);
        return (deposit(assets, receiver));
    }
```
`depositWithSignature()` is used to deposit the assets via permit and later deposits in single transaction. `depositWithSignature()` will always revert and won't work as expected as the `asset` being permitted to `address(this)` i.e `wstToken.sol` contract does not have `permit()` function in its implementation. This can be checked in `stToken.sol` [here](https://github.com/AccumulatedFinance/contracts-v2/blob/fea3cdcd7693e95c7ddcfa4c79df9b5fa715aafc/contracts/stToken.sol#L716-L741)

Therefore, assets like `rstMTRG.sol`, `stARB.sol`, `stDOJ.sol`, `stMANTA.sol`, `stMETIS.sol`, `stROSE.sol`, `stVLX.sol`, `stZETA.sol` tokens does not have `permit()` function to work correctly in `depositWithSignature()` function for depositing of stToken in vaults.

### Impact

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Accumulated-finance-0x75278bcc0fa7c9e3af98654bce195eaf3bb6a784/issues/62_
