# [H] unlimited `dStable` token can be minted without any backed collateral

## Summary
Severity: High
Chain: Smart contract
Component: dTRINITY
Published: 2025-07-02
Source: https://github.com/hats-finance/dTRINITY-0xee5c6f15e8d0b55a5eff84bb66beeee0e6140ffe/issues/309
Type: hats-finding

## Details
**Github username:** --
  **Twitter username:** --
  **HATS Profile:** ---

  **Beneficiary:** 0x3828b7Dff72E340B44f3A0270574dDE9276D5FD3
  **Submission hash (on-chain):** 0x12385e758a4345fd4547f302329686dc4ed1e74e31df76ad78afafca2949b6aa
  **Severity:** high
  
  **Description:**
  The `issueUsingExcessCollateral()` function in the `Issuer` contract is supposed to mint `dStable` only when there’s extra collateral. But if any address with the `INCENTIVES_MANAGER_ROLE` can call this function and set the receiver to the `amoManager` contract. This lets them mint unlimited `dStable` tokens without real collateral backing.

The `circulatingDstable()` function:
```solidity
function circulatingDstable() public view returns (uint256) {
        uint256 totalDstable = dstable.totalSupply();
        uint256 amoDstable = amoManager.totalAmoSupply();
        return totalDstable - amoDstable;
    }
```
we can see that increased `dStable` supply is deducted by return value of `totalAmoSupply()` function in `amoManager` contract.
```solidity
function totalAmoSupply() public view returns (uint256) {
        uint256 freeBalance = dstable.balanceOf(address(this));
        return freeBalance + totalAllocated;
    }
```
we can see that any increase in `dStable` supply is deducted by the value returned from `amoManager.totalAmoSupply()`. Now, if you check that function:
```solidity
function totalAmoSupply() public view returns (uint256) {
        uint256 freeBalance = dstable.balanceOf(address(this));
        return freeBalance + totalAllocated;
    }
```
It just adds up the `dStable` balance held by the `amoManager` contract and whatever is allocated. So if you mint new `dStable` directly to the `amoManager`, both `totalSupply` and `amoDstable` go up by the same amount, and the difference (circulatingDstable) stays the same.

Here’s the attack flow:

- Address with `INCENTIVES_MANAGER_ROLE` calls `issueUsingExcessCollateral()` and sets `receiver` to the `amoManager` contract, with any amount of `dStable` they want.

_Trimmed to 38 lines — full report: https://github.com/hats-finance/dTRINITY-0xee5c6f15e8d0b55a5eff84bb66beeee0e6140ffe/issues/309_
