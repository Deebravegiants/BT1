# [M] User to sell the last supply will

## Summary
Severity: Medium
Contest weight: 0.4717
Dataset id: 1757
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
BancorExchangeProvider::_getScaledAmountOut() decreases the amount out when the
token in is the supply token by the exit contribution, that is, scaledAmountOut=(scaledAmountOut*(MAX_WEIGHT-exchange.exitContribution))/MAX_WEIGHT;.
Whenever the last supply of the token is withdrawn, it will get all the reserve and store it
in scaledAmountOut, and then apply the exit contribution, leaving these funds forever
stuck, as there is 0 supply to redeem it.
In BancorExchangeProvider:345, the exchange contribution is applied regardless of there
being supply left to redeem it.
Internal pre-conditions
1. All supply must be withdrawn from the exchange.
External pre-conditions
None.
Attack Path
1. Users call Broker::swapIn(), that calls GoodDollarExchangeProvider::swapIn(),
which is the exchange contract that holds the token and reserve balances, selling
supply tokens until the supply becomes 0.
The last exit contribution will be forever stuck. This amount is unbounded and may be
very significant.

## Proof of Concept
Add the following test to BancorExchangeProvider.t.sol:
```solidity
function test_POC_swapIn_whenTokenInIsToken_shouldSwapIn() public {
    BancorExchangeProvider bancorExchangeProvider = initializeBancorExchangeProvider();
    uint256 amountIn = 300_000 * 1e18;
    bytes32 exchangeId = bancorExchangeProvider.createExchange(poolExchange1);
    vm.startPrank(brokerAddress);
    uint256 amountOut = bancorExchangeProvider.swapIn(exchangeId, address(token), address(reserveToken), amountIn);
    (, , uint256 tokenSupplyAfter, uint256 reserveBalanceAfter, , ) = bancorExchangeProvider.exchanges(exchangeId);
    assertEq(amountOut, 59400e18);
    assertEq(reserveBalanceAfter, 600e18);
    assertEq(tokenSupplyAfter, 0);
    vm.expectRevert("ERR_INVALID_SUPPLY");
    bancorExchangeProvider.swapIn(exchangeId, address(token), address(reserveToken), 1e18);
}
```

## Recommendation
The specific mitigation depends on the design.
