# [H] Frontrunning attacks by the `owner`

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
#### Description

There are few possible attack vectors by the owner:

1. All strategies have fees from rewards. In addition to that, the PancakeSwap strategy has deposit fees. The default deposit fees equal zero; the maximum is limited to 5%:


    **wheat-v1-core-audit/contracts/PancakeSwapCompoundingStrategyToken.sol:L29-L33**
    ```solidity
    uint256 constant MAXIMUM_DEPOSIT_FEE = 5e16; // 5%
    uint256 constant DEFAULT_DEPOSIT_FEE = 0e16; // 0%
    
    uint256 constant MAXIMUM_PERFORMANCE_FEE = 50e16; // 50%
    uint256 constant DEFAULT_PERFORMANCE_FEE = 10e16; // 10%
    ```
    
    When a user deposits tokens, expecting to have zero deposit fees, the `owner` can frontrun the deposit and increase fees to 5%. If the deposit size is big enough, that may be a significant amount of money.

2. In the `gulp` function, the reward tokens are exchanged for the reserve tokens on the `exchange`:


      **wheat-v1-core-audit/contracts/PancakeSwapCompoundingStrategyToken.sol:L218-L244**
      ```solidity
      function gulp(uint256 _minRewardAmount) external onlyEOAorWhitelist nonReentrant
      {
      	uint256 _pendingReward = _getPendingReward();
      	if (_pendingReward > 0) {
      		_withdraw(0);
      	}
      	{
      		uint256 _totalReward = Transfers._getBalance(rewardToken);
      		uint256 _feeReward = _totalReward.mul(performanceFee) / 1e18;
      		Transfers._pushFunds(rewardToken, collector, _feeReward);
      	}
      	if (rewardToken != routingToken) {
      		require(exchange != address(0), "exchange not set");
      		uint256 _totalReward = Transfers._getBalance(rewardToken);
      		Transfers._approveFunds(rewardToken, exchange, _totalReward);
      		IExchange(exchange).convertFundsFromInput(rewardToken, routingToken, _totalReward, 1);
      	}
      	if (routingToken != reserveToken) {
      		require(exchange != address(0), "exchange not set");
      		uint256 _totalRouting = Transfers._getBalance(routingToken);
      		Transfers._approveFunds(routingToken, exchange, _totalRouting);
      		IExchange(exchange).joinPoolFromInput(reserveToken, routingToken, _totalRouting, 1);
      	}
      	uint256 _totalBalance = Transfers._getBalance(reserveToken);
      	require(_totalBalance >= _minRewardAmount, "high slippage");
      	_deposit(_totalBalance);
      }
      ```

      The `owner` can change the `exchange` parameter to the malicious address that steals tokens. The `owner` then calls `gulp` with `_minRewardAmount==0`, and all the rewards will be stolen. The same attack can be implemented in fee collectors and the buyback contract.

#### Recommendation

Use a timelock to avoid instant changes of the parameters.
