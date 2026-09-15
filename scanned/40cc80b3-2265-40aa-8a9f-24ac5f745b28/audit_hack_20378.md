# [H] 5.2.5 Unsafe ERC-20 transfer breaks USDT bridging inL1BlastBridge

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** High Risk

**Context:** L1BlastBridge.sol#L

**Description:** In_initiateBridgeERC20(), USDT is transferred from the user toL1BlastBridgeusingtransfer-
From():

```
IERC20(_localToken).transferFrom(_from, address(this), _amount);
```
This will revert for USDT (which is an approved USD yield token) since itstransferFrom()function does not return
abool, but theIERC20interface expects one to be returned. As such, users will not be able to bridge USDT for
USDB.

**Recommendation:** Consider handling all ERC-20 token operations with OpenZeppelin'sSafeERC20library, which
is what Optimism'sStandardBridgedoes.

It's also best to use safeTransfer()/safeTransferFrom() for the following instances of trans-
fer()/transferFrom()since they might not work for future yield tokens:

- Insurance.sol#L
- WithdrawalQueue.sol#L
- L1BlastBridge.sol#L
- L1BlastBridge.sol#L
