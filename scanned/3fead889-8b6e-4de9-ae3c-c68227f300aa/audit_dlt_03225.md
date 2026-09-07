# [M] Approved gscApprove allowance to an address may not able to be decreased

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-07-arcade
Published: 2023-07-25
Source: https://github.com/code-423n4/2023-07-arcade-findings/issues/58
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2023-07-arcade/blob/f8ac4e7c4fdea559b73d9dd5606f618d4e6c73cd/contracts/ArcadeTreasury.sol#L189-L201


# Vulnerability details

## Impact
Approved gscApprove allowance to an address may not able to be decreased.

## Proof of Concept
**GSC_CORE_VOTING_ROLE** calls [gscApprove(...)]() function to approve tokens to be pulled from the treasury:
```
    function gscApprove(
        address token,
        address spender,
        uint256 amount
    ) external onlyRole(GSC_CORE_VOTING_ROLE) nonReentrant {
        if (spender == address(0)) revert T_ZeroAddress("spender");
        if (amount == 0) revert T_ZeroAmount();


        // Will underflow if amount is greater than remaining allowance
        gscAllowance[token] -= amount;


        _approve(token, spender, amount, spendThresholds[token].small);
    }
```
Each approval will decrease the `gscAllowance[token]` by the approved allowance amount, this is problematic as **GSC_CORE_VOTING_ROLE** may not able to decrease the approved allowance.

Consider the following scenario:
1. `gscAllowance[token]` is 100;
2. **GSC_CORE_VOTING_ROLE** calls **gscApprove(...)** to give 60 allowance to a third party;
3. `gscAllowance[token]` is 40 now;
4. Later **GSC_CORE_VOTING_ROLE** finds the approved allowance is a bit too high and want to decrease the allowance to 50;
5. **gscApprove(...)** is called again but the ransaction reverts due to underflow error (`gscAllowance[token]` is less than 50)


_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-07-arcade-findings/issues/58_
