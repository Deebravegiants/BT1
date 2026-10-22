# [H] Tokens received from Curve's remove_liquidit

## Summary
Severity: High
Contest weight: 0.7801
Dataset id: 17604
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Curve controller's canRemoveLiquidity() should return all the underlying tokens as tokensIn rather than only the tokens with minAmount>0.
https://github.com/sentimentxyz/controller/blob/a2ddbcc00f361f733352d9c51457b4ebb999c8ae/src/curve/StableSwap2PoolController.sol#L129-L152
```solidity
function canRemoveLiquidity(address target, bytes calldata data)
    internal
    view
    returns (bool, address[] memory, address[] memory)
{
    (,uint256[2] memory amounts) = abi.decode(
        data[4:],
        (uint256, uint256[2])
    );
    address[] memory tokensOut = new address[](1);
    tokensOut[0] = target;
    uint i; uint j;
    address[] memory tokensIn = new address[](2);
    while(i < 2) {
        if(amounts[i] > 0)
            tokensIn[j++] = IStableSwapPool(target).coins(i);
        unchecked { ++i; }
    }
    assembly { mstore(tokensIn, j) }
    return (true, tokensIn, tokensOut);
}
```
The amounts in Curve controller's canRemoveLiquidity() represent the "Minimum amounts of underlying coins to receive", which is used for slippage control.
At L144-149, only the tokens that specified a minAmount > 0 will be added to the tokensIn list, which will later be added to the account's assets list.
We believe this is wrong as regardless of the minAmount remove_liquidity() will always receive all the underlying tokens.
Therefore, it should not check and only add the token when it's minAmount > 0.
When the user set _min_amounts = 0 while removing liquidity from Curve and the withdrawn tokens are not in the account's assets list already, the user may get liquidated sooner than expected as RiskEngine.sol_getBalance() only counts in the assets in the assets list.

## Recommendation
canRemoveLiquidity() can be changed to:
```solidity
function canRemoveLiquidity(address target, bytes calldata data)
    internal
    view
    returns (bool, address[] memory, address[] memory)
{
    address[] memory tokensOut = new address[](1);
    tokensOut[0] = target;
    address[] memory tokensIn = new address[](2);
    tokensIn[0] = IStableSwapPool(target).coins(0);
    tokensIn[1] = IStableSwapPool(target).coins(1);
    return (true, tokensIn, tokensOut);
}
```
Confirmed fix.
