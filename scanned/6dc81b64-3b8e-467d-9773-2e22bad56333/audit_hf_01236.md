# [M] Component asset could be different than node asset

## Summary
Severity: Medium
Contest weight: 0.0790
Dataset id: 5672
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Functions ERC4626Router::_deposit() and ERC7540Router::_requestDeposit() rely on the component to retrieve the asset address. It is never checked this asset is the same as the node asset. There could be a difference due to a mistake or the component could be malicious and return a wrong asset on purpose.

## Recommendation
In ERC4626Router::_deposit() use the node.asset():
- IERC4626(vault).asset()
+ INode(node).asset()
In ERC7540Router::_requestDeposit() also use the node.asset():
- IERC4626(component).asset()
+ INode(node).asset()
When adding components, check the component.asset() == node.asset(). This could be done one or both of these:
• setErc4626() / setErc7540().
• setWhitelistStatus() / batchSetWhitelistStatus().
To be optimally flexible use a virtual function so a router can override if necessary.
