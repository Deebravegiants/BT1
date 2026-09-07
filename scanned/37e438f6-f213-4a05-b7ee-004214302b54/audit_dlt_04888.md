# [M] Can transfer position to 0 address

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-11-bullvbear
Published: 2022-11-21
Source: https://github.com/sherlock-audit/2022-11-bullvbear-judging/issues/84
Type: sherlock-finding

## Details
dipp

medium

# Can transfer position to 0 address

## Summary

The ```transferPosition``` function in ```BvbProtocol.sol``` does not check if the ```recipient``` is ```address(0)```.

## Vulnerability Detail

In the ```transferPosition``` function in ```BvbProtocol.sol```, a bull/bear is able to transfer their position to a ```recipient``` address. Since the function does not check if recipient is address(0), a user is allowed to transfer their position to address(0). This could have unintended consequences in the protocol.

The test code below shows how this is possible.

Test code added to ```TransferPosition.t.sol```:
```solidity
    function testCanTransferPositionTo0Address() public {
        BvbProtocol.Order memory order = defaultOrder();

        bytes32 orderHash = bvb.hashOrder(order);
        bytes memory signature = signOrder(bullPrivateKey, order);
        bvb.matchOrder(order, signature);

        bvb.transferPosition(orderHash, false, address(0));

        assertEq(bvb.bears(uint(orderHash)), address(0), "Transferred bear position to address(0)");
    }
```

## Impact

Users who tansfer their postions to address(0) could have their assets stuck in the contract.

## Code Snippet

[BvbProtocol.sol:transferPosition#L521-L538](https://github.com/sherlock-audit/2022-11-bullvbear/blob/main/bvb-protocol/src/BvbProtocol.sol#L521-L538):

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-11-bullvbear-judging/issues/84_
