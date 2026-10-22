# [H] Users' funds could be stolen or locked by

## Summary
Severity: High
Contest weight: 0.7950
Dataset id: 20199
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Users' funds could be stolen or locked by malicious or rogue owners.
In the contest's README, the following was mentioned.
Q: Is the admin/owner of the protocol/contracts TRUSTED or RESTRICTED?
restricted. the owner should not be able to steal funds.
It was understood that the owner is not "trusted" and should not be able to steal funds. Thus, it is fair to assume that the sponsor is keen to know if there are vulnerabilities that could allow the owner to steal funds or, to a lesser extent, lock the user's funds.
However, based on the review of the codebase, there are still some "loopholes" that the owner can exploit to steal funds or indirectly cause losses to the users. Following is a list of methods/tricks to do so.
Method 1 - Use the vulnerable withdrawNative function
Once the user's order is fulfilled, the swapped ETH/WETH will be sent to the contract awaiting the user's claim. However, the owner can call the withdrawNative function, which will forward all the Native ETH and Wrapped ETH in the contract to the owner's address due to another bug ("Lack of segregation between users' assets and collected fees resulting in loss of funds for the users") that I
Method 2 - Add a malicious custom price feed
rders/src/LimitOrderRegistry.sol#L482
File: LimitOrderRegistry.sol
```solidity
function setFastGasFeed(address feed) external onlyOwner {
    fastGasFeed = feed;
}
```
The owner can create a malicious price feed contract and configure the LimitOrderRegistry to use it by calling the setFastGasFeed function.
rders/src/LimitOrderRegistry.sol#L914
File: LimitOrderRegistry.sol
```solidity
function performUpkeep(bytes calldata performData) external {
    (UniswapV3Pool pool, bool walkDirection, uint256 deadline) = abi.decode(
        performData,
        (UniswapV3Pool, bool, uint256)
    );
    if (address(poolToData[pool].token0) == address(0)) revert LimitOrderRegistry__PoolNotSetup(address(pool));
    PoolData storage data = poolToData[pool];
    // Estimate gas cost.
    uint256 estimatedFee = uint256(upkeepGasLimit * getGasPrice());
```
When fulfilling an order, the getGasPrice() function will fetch the gas price (e.g., 100000 ETH), causing the estimatedFee to be extremely high. When users attempt to claim the order, they will be forced to pay an outrageous fee, which the users cannot afford to do so. Thus, the users have to forfeit their orders, and they will lose their swapped tokens.
Users' funds could be stolen or locked by malicious or rogue owners.

## Recommendation
Consider implementing the following measures to reduce the risk of malicious/rogue owners from stealing or locking the user's funds.
1) To mitigate the issue caused by the vulnerable withdrawNative function. Refer to finding: "Lack of segregation between users' assets and collected fees resulting in loss of funds for the users".
2) To mitigate the issue of the owner adding a malicious custom price feed, consider performing some sanity checks against the value returned from the price feed. For instance, it should not be larger than the MAX_GAS_PRICE constant. If it is larger than MAX_GAS_PRICE constant, fallback to the user-defined gas feed, which is constrained to be less than MAX_GAS_PRICE.
