# [H] A malicious user can attack keeper run out of gas by cancel_dca_order

## Summary
Severity: High
Reporter: kutugu
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/94a68e49971bc6942c75da76720f7170d46c0150/unstoppable-dex-audit/contracts/spot-dex/Dca.vy#L190
Type: audit-issue

## Details
# A malicious user can attack keeper run out of gas by cancel_dca_order

## Summary

- The protocol allows users to create a large number of orders without conditions, only check allowance
- When keeper executes orders, if user's balance or allowance is less than the execution condition, keeper needs _cancel_dca_order
- cleanup_order traverses all of the user's orders sequentially, without gas optimizations such as binary lookup
- dca_order is executed in batches. The previous batch does not call _cancel_dca_order, keeper cannot simulate this branch's gas cost

The above conditions combine to form an attack method: malicious users temporarily modify balance or allowance to make the keeper clear order and exhaust gas of the keeper.
In particular, considering that the keeper bot is unable to perceive this attack in time, the keeper bot is repeatedly attacked and the fund is exhausted.

## Vulnerability Detail

A general attack flow is as follows:
1. Malicious user creates a large number of invalid orders in advance, and finally create a valid order
2. Keeper bot listen for this tx in the mempool，no anomalies were found in the local simulation: gas cost normal and profitable
3. Keeper bot sends transactions, sniper user listens to tx, and frontrun to set allowance to 0
4. Keeper bot's tx run out of gas because of cleanup_order

User attack costs are small, by repeating the above process, the keeper bot may run out of funds.
By the way, it is also possible to attack keeper in spot-dex via the ERC777 token. But this attack involves a small variety of tokens, which keeper may not support.

Attack gas cost testing:
```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.0;

import "forge-std/Test.sol";

contract CounterTest is Test {
    bytes32[] public dca_orders;
    bytes32 constant flag = bytes32(abi.encodePacked(uint256(1024)));

    function setUp() public {
        for (uint256 i = 1; i <= 1024; i++) {
            dca_orders.push(bytes32(abi.encodePacked(i)));
        }
    }

    function testGas() public {
        bytes32[] memory orders = dca_orders;

        for (uint256 i; i < 1024; i++) {
            if (orders[i] == flag) {
                uint256 newLen = orders.length - 1;
                orders[i] = orders[newLen];
                assembly {
                    mstore(orders, newLen)
                }
                break;
            }
            if (i == orders.length - 1) {
                revert();
            }
        }

        dca_orders = orders;
    }
}
```

```shell
[PASS] testGas() (gas: 2851713)
Traces:
  [2851713] CounterTest::testGas()
    └─ ← ()
```

## Impact

keeper bot can be sniped run out of funds, causing others to be reluctant to maintain keeper, so protocol don't work efficiently

## Code Snippet

- https://github.com/sherlock-audit/2023-06-unstoppable/blob/94a68e49971bc6942c75da76720f7170d46c0150/unstoppable-dex-audit/contracts/spot-dex/Dca.vy#L190
- https://github.com/sherlock-audit/2023-06-unstoppable/blob/94a68e49971bc6942c75da76720f7170d46c0150/unstoppable-dex-audit/contracts/spot-dex/Dca.vy#L305

## Tool used

Manual Review

## Recommendation

Use the sorted orderList + binary search; Or transfer the cost of cancel_dca_order to the user
