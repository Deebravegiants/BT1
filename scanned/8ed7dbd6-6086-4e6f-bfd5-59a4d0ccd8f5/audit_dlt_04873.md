# [M] Unbounded loop can run out of gas

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-11-bullvbear
Published: 2022-11-21
Source: https://github.com/sherlock-audit/2022-11-bullvbear-judging/issues/139
Type: sherlock-finding

## Details
Deivitto

medium

# Unbounded loop can run out of gas

## Summary
Unbounded loop can run out of gas
## Vulnerability Detail

## Impact
There are no bounds on the number of orders in the loop, this can run out of gas due to cost of the operations.
## Code Snippet
https://github.com/sherlock-audit/2022-11-bullvbear/blob/main/bvb-protocol/src/BvbProtocol.sol#L546-L556

    function batchMatchOrders(Order[] calldata orders, bytes[] calldata signatures) external returns (uint[] memory) {
        require(orders.length == signatures.length, "INVALID_ORDERS_COUNT");

        uint[] memory contractIds = new uint[](orders.length);

        for (uint i; i<orders.length; i++) {
            contractIds[i] = matchOrder(orders[i], signatures[i]);
        }

        return contractIds;
    }


https://github.com/sherlock-audit/2022-11-bullvbear/blob/main/bvb-protocol/src/BvbProtocol.sol#L563-L569

    function batchSettleContracts(Order[] calldata orders, uint[] calldata tokenIds) external {
        require(orders.length == tokenIds.length, "INVALID_ORDERS_COUNT");

        for (uint i; i<orders.length; i++) {
            settleContract(orders[i], tokenIds[i]);
        }
    }


_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-11-bullvbear-judging/issues/139_
