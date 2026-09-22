# [H] [Tomo-H1] Can withdraw all funds in the DODORouteProxy contract

## Summary
Severity: High
Chain: Smart contract
Component: 2022-11-dodo
Published: 2022-11-15
Source: https://github.com/sherlock-audit/2022-11-dodo-judging/issues/67
Type: sherlock-finding

## Details
Tomo

high

# [Tomo-H1] Can withdraw all funds in the DODORouteProxy contract

## Summary

Can withdraw all funds in the DODORouteProxy contract

## Vulnerability Detail
If the following conditions are passed in `dodoMultiSwap()`, the transaction will succeed.


1. `minReturnAmount` > 0 in `dodoMultiSwap()`
2. `assetFrom.length == splitNumber.length` in `dodoMultiSwap()`
3. The balance of `toToken` in this contract is greater than before executing `multiSwap()` in `dodoMultiSwap()`
4. `receiveAmount >= minReturnAmount` in `_routeWithdraw()`

### Example
Assume the balance of WETH = 10*8*18 USDC, WBTC = 10*10*8

1. Eve executes the `dodoMultiSwap()` as the following parameters contain
`midToken = [ETH, WBTC, ETH]`,`minReturnAmount = 1`, `assetFrom = [address(this), address(this),address(this)]`
2. Assume the value of `toTokenOriginBalance` is 10*8*18 USDC
3. Eve deposits 1 wei USDC by using  `_deposit()` to the DODORouteProxy contract
4. As you can see, there are no check in the `multiSwap()` parameters.
5. Also, the only state variables used in this function are `curTotalAmount` and `totalWeight`. Other values depend on user input.
6. Users can set the values as follows by using `abi.decode()`
- `curPoolInfo.direction` = 0
- `curPoolInfo.poolEdition` = 1
- `curPoolInfo.weight` = 100
- `curPoolInfo.adapter` = address(EveAdapter)

The EveAdapter contract is like this.
[https://gist.github.com/Tomosuke0930/09a6b31cdaacd8ffa5ae40c6b6f089ee](https://gist.github.com/Tomosuke0930/09a6b31cdaacd8ffa5ae40c6b6f089ee)

7. And then, the all WBTC token in this contract transfer to `curPoolInfo.adapter` like this.
```solidity
// L49
uint256 public totalWeight = 100;

function _multiSwap(/* ... */) internal {
		/* ... */
		uint256 curTotalAmount = IERC20(midToken[i]).tokenBalanceOf(assetFrom[i - 1]);
		uint256 curTotalWeight = totalWeight;
		if (assetFrom[i - 1] == address(this)) {
		  uint256 curAmount = curTotalAmount * curPoolInfo.weight / curTotalWeight ;
                 /// curTotalAmount = 10*10*8,  curPoolInfo.weight = 100, curTotalWeight 100  
		  if (curPoolInfo.poolEdition == 1) {
		      //For using transferFrom pool (like dodoV1, Curve), pool call transferFrom function to get tokens from adapter
		      IERC20(midToken[i]).transfer(curPoolInfo.adapter, curAmount);
		/* ... */
	}
}
```

8. And Eve deposits 1 wei USDC by using  `_multiSwap()`  to the DODORouteProxy contract
9. Next, Eve can pass this checking.

```solidity
require(receiveAmount >= minReturnAmount, "DODORouteProxy: Return amount is not enough");
/// receiveAmount = 2, minReturnAmount = 1
```

10. Finally, Eve gets all WBTC in this contract using 2 wei USDC

## Impact

All tokens in this contract can transfer by small amount tokens

## Code Snippet

[https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/SmartRoute/DODORouteProxy.sol#L313-L383](https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/SmartRoute/DODORouteProxy.sol#L313-L383)

```solidity
/// @notice split version, describes one token path with several pools each time. Called one token pair with several pools "one split"
/// @param splitNumber record pool number in one split, determine sequence(poolInfo) array subscript in transverse. Begin with 0
/// for example, [0,1, 3], mean the first split has one(1 - 0) pool, the second split has 2 (3 - 1) pool
/// @param midToken middle token set, record token path in order. 
/// Specially midToken[1] is WETH addresss when fromToken is ETH. Besides midToken[1] is also fromToken 
/// Specially midToken[length - 2] is WETH address and midToken[length -1 ] is ETH address when toToken is ETH. Besides midToken[length -1]
/// is the last toToken and midToken[length - 2] is common second last middle token.
/// @param assetFrom asset Address（pool or proxy）describe pool adapter's receiver address. Specially assetFrom[0] is deposit receiver before all
/// @param sequence PoolInfo sequence, describe each pool's attributions, ordered by spiltNumber
/// @param feeData route fee info, bytes decode into broker and brokerFee, determine rebate proportion, brokerFee in [0, 1e18]
function dodoMutliSwap(
    uint256 fromTokenAmount,
    uint256 minReturnAmount,
    uint256[] memory splitNumber,  
    address[] memory midToken,
    address[] memory assetFrom,
    bytes[] memory sequence, 
    bytes memory feeData,
    uint256 deadLine
) external payable judgeExpired(deadLine) returns (uint256 receiveAmount) {
    address toToken = midToken[midToken.length - 1];
    {
    require(
        assetFrom.length == splitNumber.length,
        "DODORouteProxy: PAIR_ASSETTO_NOT_MATCH"
    );
    require(minReturnAmount > 0, "DODORouteProxy: RETURN_AMOUNT_ZERO");
    uint256 _fromTokenAmount = fromTokenAmount;
    address fromToken = midToken[0];

    uint256 toTokenOriginBalance;
    if(toToken != _ETH_ADDRESS_) {
        toTokenOriginBalance = IERC20(toToken).universalBalanceOf(address(this));
    } else {
        toTokenOriginBalance = IERC20(_WETH_).universalBalanceOf(address(this));
    }

    // transfer in fromToken
    _deposit(
        msg.sender,
        assetFrom[0],
        fromToken,
        _fromTokenAmount,
        fromToken == _ETH_ADDRESS_
    );

    // swap
    _multiSwap(midToken, splitNumber, sequence, assetFrom);

    // calculate toToken amount
    if(toToken != _ETH_ADDRESS_) {
        receiveAmount = IERC20(toToken).universalBalanceOf(address(this)) - (
            toTokenOriginBalance
        );
    } else {
        receiveAmount = IERC20(_WETH_).universalBalanceOf(address(this)) - (
            toTokenOriginBalance
        );
    }
    }
    // distribute toToken
    _routeWithdraw(toToken, receiveAmount, feeData, minReturnAmount);

    emit OrderHistory(
        midToken[0], //fromToken
        midToken[midToken.length - 1], //toToken
        msg.sender,
        fromTokenAmount,
        receiveAmount
    );
}
```

## Tool used

Manual Review

## Recommendation

Check the balance of tokens used in `assetFrom[]` to see if they have been improperly transferred.

Also, creating whitelisted to restrict the `curPoolInfo.adapter` and `curPoolInfo.pool`
