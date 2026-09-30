# [M] Attackers can sandwich their own trades up

## Summary
Severity: Medium
Contest weight: 0.4591
Dataset id: 22577
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Malicious users can sandwich their own SpotHedgeBaseMaker trades up to the price band cap. The SpotHedgeBaseMaker allows one to settle trades against a UniswapV3 pool. The assumption is that the pool prices tokens properly, and any imbalance in the pool is reflected in the price paid/amount received by the trader interacting with the SpotHedgeBaseMaker. This assumption is incorrect, because an attacker can sandwich their own trade, taking value out of the Perpetual system. The attacker would get a large flash loan, imbalance the pool, use the ClearingHouse to settle and opening trade, then re-balance the pool, all in the same transaction. For example, assume the actual exchange rate is $4,000/1WEth, and the attacker is able to skew it such that the exchange rate temporarily becomes $1/1WEth. The attacker opening a short of 1Eth means that the SpotHedgeBaseMaker ends up going long 1Eth, and hedges that long by swapping 1WEth for 1. The attacker ends up using 1 in margin to open the short. After the attacker unwinds the skew, they've gained 1 from the rebalance, and they can abandon the perp account worth -$4k. In reality, the attacker won't be able to skew the exchange rate by quite that much, because there's a price band check at the end of the trade, ensuring that the price indicate that the bands are anticipated to be +/- 10%. If the price bands are set to zero (the swap price must be the oracle price), then the SpotHedgeBaseMaker won't be usable at all, since uniswap charges a fee for every trade. If the bands are widened to be just wide enough to accommodate the fee, then other parts of the system, such as the OracleMaker won't work properly (see other submitted issue). Therefore, either some value will be extractable, or parts of the protocol will be broken. Because of these restrictions/limitations I've submitted this as a Medium. The SpotHedgeBaseMaker doesn't require that the sender be the Gateway/GatewayV2, so anyone can execute it directly from the ClearingHouse:
```solidity
// File: src/maker/SpotHedgeBaseMaker.sol : SpotHedgeBaseMaker.isValidSender()
#1
function isValidSender(address) external pure override returns (bool)
{
    return true;
516:
}
/src/maker/SpotHedgeBaseMaker.sol#L504-L526
```

## Recommendation
Require that SpotHedgeBaseMaker be executed by a relayer
