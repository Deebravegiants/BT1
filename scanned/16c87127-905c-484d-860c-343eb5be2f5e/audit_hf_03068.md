# [M] Must approve 0 first

## Summary
Severity: Medium
Contest weight: 0.5752
Dataset id: 17349
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability is an allowance‑reset bug that occurs when the contract attempts to set a new non‑zero ERC20 allowance without first clearing the existing allowance to zero. Certain token implementations, most notably USDT, deliberately reject a direct change from a non‑zero allowance to another non‑zero value as a protective measure against the well‑known ERC20 race condition. In the affected function the contract calls IERC20(token).approve(address(bondNFT),type(uint256).max) on each iteration without first calling approve(address(bondNFT),0). When the token enforces the zero‑first rule, the approve call reverts, causing the entire claimGovFees transaction to fail. As a result the protocol cannot transfer the newly claimed governance fees to the bondNFT for distribution, leaving user balances unchanged and fees effectively stuck in the contract. The issue manifests only when the contract interacts with tokens that implement the non‑standard approve behaviour; standard ERC20 tokens that allow direct allowance updates are unaffected. It was discovered during a manual audit when the auditor observed that the approve call could always revert for some tokens and reproduced the failure with a proof‑of‑concept that called approve(max) directly. The bug is subtle because most developers assume the ERC20 specification permits any allowance change, and the contract’s logic does not check the return value or catch the revert, making the problem easy to overlook in testing. Conceptually, the fix is to follow the safe‑approval pattern: reset the allowance to zero before setting a new non‑zero allowance, or use increaseAllowance/decreaseAllowance functions when available. Implementing this pattern ensures compatibility with all ERC20 variants, prevents transaction reverts, and guarantees that claimed fees are correctly transferred to users, preserving the intended accounting and business logic of the protocol.

## Proof of Concept
```solidity
function claimGovFees() public {
    address[] memory assets = bondNFT.getAssets();

    for (uint i=0; i < assets.length; i++) {
        uint balanceBefore = IERC20(assets[i]).balanceOf(address(this));
        IGovNFT(govNFT).claim(assets[i]);
        uint balanceAfter = IERC20(assets[i]).balanceOf(address(this));
        IERC20(assets[i]).approve(address(bondNFT), type(uint256).max); // @audit this could fail always with some tokens,
        bondNFT.distribute(assets[i], balanceAfter - balanceBefore);
    }
}
```

## Recommendation
Add an `approve(0)` before approving;

```solidity
function claimGovFees() public {
    address[] memory assets = bondNFT.getAssets();

    for (uint i=0; i < assets.length; i++) {
        uint balanceBefore = IERC20(assets[i]).balanceOf(address(this));
        IGovNFT(govNFT).claim(assets[i]);
        uint balanceAfter = IERC20(assets[i]).balanceOf(address(this));
        IERC20(assets[i]).approve(address(bondNFT), 0);
        IERC20(assets[i]).approve(address(bondNFT), type(uint256).max);
        bondNFT.distribute(assets[i], balanceAfter - balanceBefore);
    }
}
```

The Warden has shown how, due to the function approving max multiple times, certain tokens, that only allow a non-zero allowance to be set starting from zero, could revert.

Because this depends on the token implementation, but there’s a reasonable chance to believe that USDT will be used, I agree with Medium Severity.

Since the purpose of the bonds is to lock tigAsset liquidity, only tigAsset tokens will be allowed to be locked, which don’t have this issue.

**[GainsGoblin (Tigris Trade) resolved](https://github.com/code-423n4/2022-12-tigris-findings/issues/104#issuecomment-1407862000):**

Mitigation: <https://github.com/code-423n4/2022-12-tigris/pull/2#issuecomment-1419177578>
