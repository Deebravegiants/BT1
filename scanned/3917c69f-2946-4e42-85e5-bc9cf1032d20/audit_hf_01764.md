# [H] Loss of fee refund due to premature state deletion in `PerpetualVault::_handleReturn` function

## Summary
Severity: High
Contest weight: 1.0000
Dataset id: 9775
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The Gamma protocol will refund the excess execution fee to the user when the flow is finalized. However, the PerpetualVault::_handleReturn function has a flaw logic that does not properly refund fees, which causes any flow that ends with this function to be affected by this vulnerability.

The PerpetualVault::_handleReturn function is used in the withdraw and signal change flows. This function comprises the burn and refund processes. However, the burn process is called before the refund process, which causes the depositInfo[depositId] to be deleted before the refund process. Consequently, the depositInfo[depositId].executionFee is always 0, causing the refund condition to never be met.

```solidity
  function _handleReturn(uint256 withdrawn, bool positionClosed, bool refundFee) internal {
    (uint256 depositId) = flowData;
    uint256 shares = depositInfo[depositId].shares;
    uint256 amount;
    if (positionClosed) {
      amount = collateralToken.balanceOf(address(this)) * shares / totalShares;
    } else {
      uint256 balanceBeforeWithdrawal = collateralToken.balanceOf(address(this)) - withdrawn;
      amount = withdrawn + balanceBeforeWithdrawal * shares / totalShares;
    }
    if (amount > 0) {
      _transferToken(depositId, amount);
    }
    emit Burned(depositId, depositInfo[depositId].recipient, depositInfo[depositId].shares, amount);
    _burn(depositId);

    if (refundFee) {
      uint256 usedFee = callbackGasLimit * tx.gasprice;
      if (depositInfo[depositId].executionFee > usedFee) {
        try IGmxProxy(gmxProxy).refundExecutionFee(depositInfo[counter].owner, depositInfo[counter].executionFee - usedFee) {} catch {}
      }
    }

    // update global state
    delete swapProgressData;
    delete flowData;
    delete flow;
  }
```

```solidity
  function _burn(uint256 depositId) internal {
    EnumerableSet.remove(userDeposits[depositInfo[depositId].owner], depositId);
    totalShares = totalShares - depositInfo[depositId].shares;
    delete depositInfo[depositId];
  }
```

Any flows that ends with the PerpetualVault::handleReturn function by the refundFee = true will be affected by this vulnerability. Especially, the PerpetualVault::payExecutionFee function allows the user to send arbitrary amount excess the estimated execution fee without restriction. Consequently, the user will lose all fee without getting any refund and the execution fee becomes stuck in the GmxProxy contract.

Please note that although the protocol has the GmxProxy::withdrawEth function that allows owner withdraw ethers in some accident. However, this function should not be called in the normal flow.

## Proof of Concept
This PoC demonstrates withdrawing on the long one leverage vault which is one of the example flow that call the PerpetualVault::_handleReturn function to refund the execution fee.
Copy the getParaSwapDataIndexTo_Collateral function to the test/mock/MockData.sol for support swap index token back to collateral token for withdraw flow.
Copy the following test case to the test/PerpetualVault.t.sol file
Run test with forge test --mt testLossOfGasFeeRefundWhen_Withdraw --rpc-url arbitrum

```solidity
  function getParaSwapDataIndexTo_Collateral(address receiver) external pure returns (bytes memory) {
    bytes memory rev = abi.encodePacked(receiver);
    bytes memory original = hex'000000000000000000000000def171fe48cf0115b1d80b88dc8eab59176fee57000000000000000000000000000000000000000000000000287a7d29bb1d81ed000000000000000000000000000000000000000000000000000000000000006000000000000000000000000000000000000000000000000000000000000007c446c67b6d000000000000000000000000000000000000000000000000000000000000002000000000000000000000000082af49447d8a07e3bd95bd0d56f35241523fbab1000000000000000000000000000000000000000000000000287a7d29bb1d81ed00000000000000000000000000000000000000000000000000000002440be40000000000000000000000000000000000000000000000000000000002540be400000000000000000000000000919c94b69950449cea621fd6cc0cb538de79d0dd000000000000000000000000000000000000000000000000000000000000016000000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000004000000000000000000000000000000000000000000000000000000000000000078000000000000000000000000000000000000000000000000000000000679cf4ce161d4b0c6e2e4ca381c524a0776f557100000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000000200000000000000000000000000000000000000000000000000000000000002710000000000000000000000000000000000000000000000000000000000000004000000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000020000000000000000000000000af88d065e77c8cc2239327c5edb3a432268e5831000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000600000000000000000000000000000000000000000000000000000000000000002000000000000000000000000000000000000000000000000000000000000004000000000000000000000000000000000000000000000000000000000000002a000000000000000000000000058a5f0b73969800faff8556cd2187e3fce71a6cb0000000000000000000000000000000000000000000000000000000000001f40000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000800000000000000000000000000000000000000000000000000000000000000001000000000000000000000000000000000000000000000000000000000000002000000000000000000000000000000000000000000000000000000000000000070000000000000000000000001f721e2e82f6676fce4ea07a5958cf098d339e18000000000000000000000000000000000000000000000000000000000000271000000000000000000000000000000000000000000000000000000000000000a0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000e000000000000000000000000000000000000000000000000000000000000000200000000000000000000000000000000000000000000000000000000067a62e220000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000002882af49447d8a07e3bd95bd0d56f35241523fbab1af88d065e77c8cc2239327c5edb3a432268e5831000000000000000000000000000000000000000000000000000000000000000000000000369a2fdb910d432f0a07381a5e3d27572c87671300000000000000000000000000000000000000000000000000000000000007d0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000800000000000000000000000000000000000000000000000000000000000000001000000000000000000000000000000000000000000000000000000000000002000000000000000000000000000000000000000000000000000000000000000030000000000000000000000001b81d678ffb9c0263b24a97847620c99d213eb14000000000000000000000000000000000000000000000000000000000000271000000000000000000000000000000000000000000000000000000000000000a0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000c0000000000000000000000000000000000000000000000000000000000000002000000000000000000000000000000000000000000000000000000000000000400000000000000000000000000000000000000000000000000000000067a62e22000000000000000000000000000000000000000000000000000000000000002b82af49447d8a07e3bd95bd0d56f35241523fbab1000064af88d065e77c8cc2239327c5edb3a432268e583100000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000';
    bytes memory result = original;
    assembly {
      let originalPtr := add(result, 0x20)
      let replacementPtr := add(rev, 0x20)
      for {let i := 0} lt(i, mload(rev)) { i := add(i, 0x20) } {
        mstore(add(originalPtr, add(304, i)), mload(add(replacementPtr, i)))
      }
    }
    require(original.length == result.length, "fail");
    return result;
  }
```

```solidity
  function testLossOfGasFeeRefundWhen_Withdraw() external {
    address keeper = PerpetualVault(vault).keeper();
    address gmxProxy = address(PerpetualVault(vault).gmxProxy());
    uint256 gmxProxyBalBefore = gmxProxy.balance;
    address alice = makeAddr("alice");
    depositFixture(alice, 1e10);

    MarketPrices memory prices = mockData.getMarketPrices();
    bytes memory paraSwapData = mockData.getParaSwapData(vault);
    bytes[] memory swapData = new bytes[](1);
    swapData[0] = abi.encode(PROTOCOL.DEX, paraSwapData);
    vm.prank(keeper);
    PerpetualVault(vault).run(true, true, prices, swapData);

    uint256 lockTime = 1;
    PerpetualVault(vault).setLockTime(lockTime);
    vm.warp(block.timestamp + lockTime + 1);

    paraSwapData = mockData.getParaSwapDataIndexTo_Collateral(vault);
    swapData = new bytes[](1);
    swapData[0] = abi.encode(PROTOCOL.DEX, paraSwapData);
    uint256[] memory depositIds = PerpetualVault(vault).getUserDeposits(alice);
    deal(alice, 1 ether);
    vm.prank(alice);
    PerpetualVault(vault).withdraw{value: alice.balance}(alice, depositIds[0]); // alice mistakenly sent all balance of ether as execution fee

    vm.prank(keeper);
    PerpetualVault(vault).runNextAction(prices, swapData);

    // withdrawal flow is finalized
    uint8 flow = uint8(PerpetualVault(vault).flow());
    assertEq(flow, 0);
    (PerpetualVault.NextActionSelector selector, ) = PerpetualVault(vault).nextAction();
    assertEq(uint8(selector), 0);

    assertEq(alice.balance, 0); // alice loss all ether without getting any refund
    assertEq(gmxProxy.balance, gmxProxyBalBefore + 1 ether); // alices execution fee becomes stuck in the GmxProxy contract!
  }
```

## Recommendation
Within the PerpetualVault::_handleReturn function, bring the burn process to execute after refunding the execution fee process.

```diff
  function _handleReturn(uint256 withdrawn, bool positionClosed, bool refundFee) internal {
    (uint256 depositId) = flowData;
    uint256 shares = depositInfo[depositId].shares;
    uint256 amount;
    if (positionClosed) {
      amount = collateralToken.balanceOf(address(this)) * shares / totalShares;
    } else {
      uint256 balanceBeforeWithdrawal = collateralToken.balanceOf(address(this)) - withdrawn;
      amount = withdrawn + balanceBeforeWithdrawal * shares / totalShares;
    }
    if (amount > 0) {
      _transferToken(depositId, amount);
    }
    emit Burned(depositId, depositInfo[depositId].recipient, depositInfo[depositId].shares, amount);

    if (refundFee) {
      uint256 usedFee = callbackGasLimit * tx.gasprice;
      if (depositInfo[depositId].executionFee > usedFee) {
        try IGmxProxy(gmxProxy).refundExecutionFee(depositInfo[counter].owner, depositInfo[counter].executionFee - usedFee) {} catch {}
      }
    }
    _burn(depositId);

    // update global state
    delete swapProgressData;
    delete flowData;
    delete flow;
  }
```
