# [M] First user can inflatepointsPerShare and cause

## Summary
Severity: Medium
Contest weight: 0.2106
Dataset id: 17614
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
pointsPerShare can be manipulated by the first user and cause _correctPoints() to revert later.  
POINTS_MULTIPLIER is an unusually large number as a precision fix for pointsPerShare: type(uint128).max = 3.4e38.  
This makes it possible for the first user to manipulate the pointsPerShare to near type(int256).max and a later regular user can trigger the overflow of _shares * _shares * in _correctPoints().  
By manipulating the pointPerShare precisely, the attacker can make it possible for the system to run normally for a little while and only to explode after a certain amount of deposits, as the pointsPerShare will be too large by then and all the _mint and _burn will revert due to overflow in _correctPoints().  
The users who deposited before will be unable to withdraw their funds.

## Proof of Concept
1. deposit(1wei) lock for 10 mins, mint() 1 wei of shares;  
2. distributeRewards(1000e18), pointsPerShare += 1000e18 * type(uint128).max / 1 == 3e59;  
3. the victim deposit(100e18) for 1 year, mint() 150e18 shares;  
4. _shares * pointsPerShare == -150e18 * 3e59 == -4.5e+79 which exceeds type(int256).min, thus the transaction will revert.  
The attacker can also manipulate pointsPerShare to a slightly smaller number, so that _shares * pointsPerShare will only overflow after a certain amount of deposits.

## Recommendation
1. Add a minimal mint amount requirement for the first minter and send a portion of the initial shares to gov as a permanent reserve to avoid pointPerShare manipulating.  
2. Use a smaller number for POINTS_MULTIPLIER, eg, 1e12.
