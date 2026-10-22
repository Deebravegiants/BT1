# [M] The rewards distribution in the

## Summary
Severity: Medium
Contest weight: 0.6938
Dataset id: 23171
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In NFTPositionManager, users can deposit or borrow assets and earn rewards in zero. However, the distribution of these rewards is not working correctly.
Let's consider a pool, P, and an asset, A, with a current liquidityindex of 1.5.
• Two users, U1 and U2, each deposit 100 units of A into pool P. (Think of U1 and U2 as tokenIDs.)
• Let's define assetHash(P,A,false) as H.
• In the _supply function, the balance is 100, since it represents the assetamount, not shares (as seen in line57).
```solidity
function _supply(AssetOperationParams memory params) internal nonReentrant {
    pool.supply(params.asset, address(this), params.amount, params.tokenId, params.data);
    uint256 balance = pool.getBalance(params.asset, address(this), params.tokenId);
    _handleSupplies(address(pool), params.asset, params.tokenId, balance);
}
```
• The shares for these users would be calculated as 100÷1.5=66.67 shares each in the P.
Now, in the _handleSupplies function, we compute the totalsupply and balances for these users for the assetHash H.
```solidity
function _handleSupplies(address pool, address asset, uint256 tokenId, uint256 balance) internal {
    bytes32 _assetHash = assetHash(pool, asset, false); // H
    uint256 _currentBalance = _balances[tokenId][_assetHash]; // 0
    _updateReward(tokenId, _assetHash);
    _balances[tokenId][_assetHash] = balance; // 100
    _totalSupply[_assetHash] = _totalSupply[_assetHash] - _currentBalance + balance;
}
```
Those values would be as below:
• Total supply: totalSupply[H]=200
• Balances: _balances[U1][H]=_balances[U2][H]=100
After some time:
• The liquidityindex increases to 2.
• A new user, U3, deposits 110 units of A into the pool P.
• U2 makes a small withdrawal of just 1 wei to trigger an update to their balance.
Now, the totalsupply and user balances for assetHash H become:
• _balances[U1][H]=100
• _balances[U2][H]=100÷1.5×2=133.3
• _balances[U3][H]=110
• totalSupply[H]=343.3
At this point, User U1’s assetbalance in the poolP is the largest, being 1 wei more than U2's and 23.3 more than U3's. Yet, U1 receives the smallest rewards because their balance was never updated in the NFTPositionManager. In contrast, User U2 receives more rewards due to the balance update caused by withdrawing just 1 wei.
The issue:
This system is unfair because:
• User U3, who has fewer assets in the pool than U1, is receiving more rewards.
• The rewards distribution favors users who perform frequent updates (like deposits or withdrawals), which is not equitable.
The solution:
Instead of using the assetbalance as the rewards basis, we should use the shares in the pool. Here’s how the updated values would look:
• _balances[U1][H]=66.67
• _balances[U2][H]=66.67-1 wei
• _balances[U3][H]=110÷2=55
• totalSupply[H]=188.33
This way, the rewards distribution becomes fair, as it is based on actual contributions to the pool.

## Recommendation
```solidity
function _supply(AssetOperationParams memory params) internal nonReentrant {
    pool.supply(params.asset, address(this), params.amount, params.tokenId, params.data);
    uint256 balance = pool.getBalanceRaw(params.asset, address(this), params.tokenId).supplyShares;
    _handleSupplies(address(pool), params.asset, params.tokenId, balance);
}
```
The same applies to the _borrow, _withdraw, and _repay functions.
