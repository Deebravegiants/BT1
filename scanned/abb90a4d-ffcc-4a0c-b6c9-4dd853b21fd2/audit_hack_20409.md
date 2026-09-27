# [M] 5.1.2 Fee on transfer tokens

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Medium Risk
**Context:** PolygonZkEVMBridge.sol#L
**Description:** The bridge contract will not work properly with a fee on transfer tokens

1. User A bridges a fee on transfer Token A from Mainnet to Rollover R1 for amount X.
2. In that caseX-feeswill be received by bridge contract on Mainnet but the deposit receipt of the full amount
    Xwill be stored in Merkle.
3. The amount is claimed in R1 and a new TokenPair for Token A is generated and the full amountXis minted
    to User A
4. Now the full amount is bridged back again to Mainnet
5. When a claim is made on Mainnet then the contract tries to transfer amountXbut since it received the amount
    X-feesit will use the amount from other users, which eventually causes DOS for other users using the same
    token
**Recommendation:** Use the exact amount which is transferred to the contract which can be obtained using below
sample code


```
uint256 balanceBefore = IERC20Upgradeable(token).balanceOf(address(this));
IERC20Upgradeable(token).safeTransferFrom(address(msg.sender), address(this), amount);
uint256 balanceAfter = IERC20Upgradeable(token).balanceOf(address(this));
uint256 transferedAmount = balanceAfter - balanceBefore;
// if you dont want to support fee on transfer token use below:
require (transferedAmount == amount, ...);
// use transferedAmount if you want to support fee on transfer token
```
**Polygon-Hermez:** Solved in PR 87. To protect against reentrancy with erc777 tokens, a check for reentrancy
MUST be added.
Solved in PR 91.
**Spearbit:** Verified.
