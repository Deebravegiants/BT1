# [M] Allo#_fundPool

## Summary
Severity: Medium
Contest weight: 0.5877
Dataset id: 20470
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Let's see the code of the _fundPool function:
```solidity
function _fundPool(uint256 _amount, uint256 _poolId, IStrategy _strategy)
    internal
{
    uint256 feeAmount;
    uint256 amountAfterFee = _amount;
    Pool storage pool = pools[_poolId];
    address _token = pool.token;
    if (percentFee > 0) {
        feeAmount = (_amount * percentFee) / getFeeDenominator();
        amountAfterFee -= feeAmount;
        _transferAmountFrom(_token, TransferData({from: msg.sender, to: treasury, amount: feeAmount}));
    }
    _transferAmountFrom(_token, TransferData({from: msg.sender, to: address(_strategy), amount: amountAfterFee}));
    _strategy.increasePoolAmount(amountAfterFee);
    emit PoolFunded(_poolId, amountAfterFee, feeAmount);
}
```

The feeAmount is calculated as follows:
```solidity
feeAmount = (_amount * percentFee) / getFeeDenominator();
```

where getFeeDenominator returns 1e18 and percentFee is represented like that: 1e18 the variable). Let's say the pool uses a token like GeminiUSD which is a token with 300M+ market cap, so it's widely used, and percentFee == 1e15 (0.1%) A user could circumvent the fee by depositing a relatively small amount. In our example, he can deposit 9 GeminiUSD. In that case, the calculation will be:
```solidity
feeAmount = (_amount * percentFee) / getFeeDenominator() = (9e2 * 1e15) / 1e18 = 9e17/1e18 = 9/10 = 0;
```

So the user ends up paying no fee. There is nothing stopping the user from funding his pool by invoking the fundPool with such a small amount as many times as he needs to fund the pool with whatever amount he chooses, circumventing the fee. Especially with the low gas fees on L2s on which the protocol will be deployed, this will be a viable method to fund a pool without paying any fee to the protocol. The protocol doesn't collect fees from pools with low decimal tokens.

## Recommendation
Add a minFundAmount variable and check for it when funding a pool.
