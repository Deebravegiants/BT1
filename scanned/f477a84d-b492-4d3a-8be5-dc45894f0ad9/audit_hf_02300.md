# [M] Revisited Price Calculation in AlphaKeysToken

## Summary
Severity: Medium
Contest weight: 0.4270
Dataset id: 12553
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The NBC protocol issues keys as ERC20-compliant tokens, ensuring that each user has their own ERC20 contracts for keys. To issue a new key on NBC, the approval from the NBC admin is required to verify that the Twitter data and user information match. In the process of examining the issued keys, we notice the trade price calculation should be improved.
To elaborate, we show below the related getPriceV2() routine. It has a rather straightforward logic in pricing the share purchase. However, it should be revisited to compute sum1 as 0 when supply <= NUMBER_UNIT_PER_ONE_ETHER (line 172). Note the same adjustment should be made for sum2 as well (line 179).
```solidity
function getPriceV2(
    uint256 supply,
    uint256 amount
) internal pure returns (uint256) {
    uint256 sum1 = supply == 0
        ? 0
        : ((supply - NUMBER_UNIT_PER_ONE_ETHER) * supply * (2 * (supply - NUMBER_UNIT_PER_ONE_ETHER) + NUMBER_UNIT_PER_ONE_ETHER)) / 6;
    uint256 sum2 = supply == 0 && amount == 1
        ? 0
        : ((supply - NUMBER_UNIT_PER_ONE_ETHER + amount) * (supply + amount) * (2 * (supply - NUMBER_UNIT_PER_ONE_ETHER + amount) + NUMBER_UNIT_PER_ONE_ETHER)) / 6;
    uint256 summation = sum2 - sum1;
    return (summation * ONE_ETHER) / PRICE_KEYS_DENOMINATOR / (NUMBER_UNIT_PER_ONE_ETHER * NUMBER_UNIT_PER_ONE_ETHER * NUMBER_UNIT_PER_ONE_ETHER);
}
```

## Recommendation
Improve the above routine by funding the extra payment back to the buyer.
