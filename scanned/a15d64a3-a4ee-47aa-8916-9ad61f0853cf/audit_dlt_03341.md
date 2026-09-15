# [M] Overprivileged admin can grant unlimited WETH

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-06-canto
Published: 2022-06-21
Source: https://github.com/code-423n4/2022-06-canto-findings/issues/241
Type: code-finding

## Details
# Lines of code

https://github.com/Plex-Engineer/lending-market/blob/755424c1f9ab3f9f0408443e6606f94e4f08a990/contracts/Comptroller.sol#L1376


# Vulnerability details

## Impact
Admin can `_grantComp()` to any address using any amount and drain the contract.

## Proof of Concept

If admin key gets compromised there is no timelock, no amount boundaries and no address limitations to prevent the assets to be drained immediately to the attackers address.

## Tools Used
Manual Review.

## Recommended Mitigation Steps
There is a few suggestions that could help mitigate this issue:
Implement timelock for `_grantComp()`
Implement hard coded recipient so funds cannot be arbitrarily sent to any address.
Implement a limit to the amount that can be granted.

Here is a reference to a past submission where this issue has been made by team Watchpug: https://github.com/code-423n4/2022-01-insure-findings/issues/271
