# [H] In Redeemer.sol contract, allowance is not properly given to underlying contract before redeeming.

## Summary
Severity: High
Chain: Smart contract
Component: 2022-10-illuminate
Published: 2022-11-10
Source: https://github.com/sherlock-audit/2022-10-illuminate-judging/issues/151
Type: sherlock-finding

## Details
ctf_sec

high

# In Redeemer.sol contract, allowance is not properly given to underlying contract before redeeming.

## Summary

In Redeemer.sol contract, allowance is not properly given to underlying contract before redeeming.

## Vulnerability Detail

Note that in Lender.sol, we have this function

```solidity
    /// @notice bulk approves the usage of addresses at the given ERC20 addresses.
    /// @dev the lengths of the inputs must match because the arrays are paired by index
    /// @param u array of ERC20 token addresses that will be approved on
    /// @param a array of addresses that will be approved
    /// @return true if successful
    function approve(address[] calldata u, address[] calldata a)
        external
        authorized(admin)
        returns (bool)
    {
        for (uint256 i; i != u.length; ) {
            IERC20 uToken = IERC20(u[i]);
            if (address(0) != (address(uToken))) {
                Safe.approve(uToken, a[i], type(uint256).max);
            }
            unchecked {
                ++i;
            }
        }
        return true;
    }
```


_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-10-illuminate-judging/issues/151_
