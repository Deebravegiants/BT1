# [H] Deposits on long one leverage vault don't actually finalize the flow, leading to a Denial of Service (DoS)

## Summary
Severity: High
Contest weight: 0.9599
Dataset id: 9774
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The Gamma protocol utilizes the flow and nextAction to keep track of the current flow progress. The current flow needs to be finalized before doing another flow. However, for the long one leverage vault, the deposit flow don't actually finalize the flow, which prevents another flow from proceeding, leading to DoS.

When the position is opened, the PerpetualVault::deposit function will set the flow to FLOW.DEPOSIT and the nextAction to INCREASE_ACTION, then leaves the Keeper call PerpetualVault::runNextAction function to finalize the deposit flow.

```solidity
  function deposit(uint256 amount) external nonReentrant payable {
    _noneFlow();
    if (depositPaused == true) {
      revert Error.Paused();
    }
    if (amount < minDepositAmount) {
      revert Error.InsufficientAmount();
    }
    if (totalDepositAmount + amount > maxDepositAmount) {
      revert Error.ExceedMaxDepositCap();
    }
    flow = FLOW.DEPOSIT;
    collateralToken.safeTransferFrom(msg.sender, address(this), amount);
    counter++;
    depositInfo[counter] = DepositInfo(amount, 0, msg.sender, 0, block.timestamp, address(0));
    totalDepositAmount += amount;
    EnumerableSet.add(userDeposits[msg.sender], counter);

    if (positionIsClosed) {
      MarketPrices memory prices;
      _mint(counter, amount, false, prices);
      _finalize(hex'');
    } else {
      _payExecutionFee(counter, true);
      // mint share token in the NextAction to involve off-chain price data and improve security
      nextAction.selector = NextActionSelector.INCREASE_ACTION;
      nextAction.data = abi.encode(beenLong);
    }
  }
```

However, if the vault is long one leverage, when the PerpetualVault::runNextAction function calls the PerpetualVault::_runSwap function, if the given metadata set to swap only on ParaSwap, the process just mints the shares without finalizing the deposit flow. Consequently, the flow remains unfinalized.

```solidity
  function runNextAction(MarketPrices memory prices, bytes[] memory metadata) external nonReentrant gmxLock {
    _onlyKeeper();
    Action memory _nextAction = nextAction;
    delete nextAction;
    if (nextAction.selector == NextActionSelector.INCREASEACTION) {
      (bool isLong) = abi.decode(nextAction.data, (bool));

      if (isLongOneLeverage(isLong)) {
        _runSwap(metadata, true, prices);
      } else {
    
    ...
  }
```

```solidity
  function _runSwap(bytes[] memory metadata, bool isCollateralToIndex, MarketPrices memory prices) internal returns (bool completed) {
    if (metadata.length == 0) {
      revert Error.InvalidData();
    }
    if (metadata.length == 2) {
      (PROTOCOL _protocol, bytes memory data) = abi.decode(metadata[0], (PROTOCOL, bytes));
      if (_protocol != PROTOCOL.DEX) {
        revert Error.InvalidData();
      }
      swapProgressData.swapped = swapProgressData.swapped + _doDexSwap(data, isCollateralToIndex);
      
      (_protocol, data) = abi.decode(metadata[1], (PROTOCOL, bytes));
      if (_protocol != PROTOCOL.GMX) {
        revert Error.InvalidData();
      }

      _doGmxSwap(data, isCollateralToIndex);
      return false;
    } else {
      if (metadata.length != 1) {
        revert Error.InvalidData();
      }
      (PROTOCOL _protocol, bytes memory data) = abi.decode(metadata[0], (PROTOCOL, bytes));
      if (_protocol == PROTOCOL.DEX) {
        uint256 outputAmount = _doDexSwap(data, isCollateralToIndex);
        
        // update global state
        if (flow == FLOW.DEPOSIT) {
          // last depositId equals with counter because another deposit is not allowed before previous deposit is completely processed
          _mint(counter, outputAmount + swapProgressData.swapped, true, prices);
        } else if (flow == FLOW.WITHDRAW) {
          _handleReturn(outputAmount + swapProgressData.swapped, false, true);
        } else {
          // in the flow of SIGNAL_CHANGE, if isCollateralToIndex is true, it is opening position, or closing position
          _updateState(!isCollateralToIndex, isCollateralToIndex);
        }
        
        return true;
      } else {
        _doGmxSwap(data, isCollateralToIndex);
        return false;
      }
    }
  }
```

This causes a Denial of Service (DoS) for the long one leverage vault, rendering the vault useless since it cannot proceed with another flow.

Please note that although the protocol had the PerpetualVault::cancelFlow and PerpetualVault::setVaultState functions that allow forcing cancellation or setting the flow states directly. However, these functions are not designed for this situation.

## Proof of Concept
Copy the following test case to the test/PerpetualVault.t.sol file
Run test with forge test --mt testRevert1xLongPositionWithMultipleDeposits --rpc-url arbitrum

```solidity
  function testRevert1xLongPositionWithMultipleDeposits() external {
    address keeper = PerpetualVault(vault).keeper();
    address alice = makeAddr("alice");
    depositFixture(alice, 1e10);

    MarketPrices memory prices = mockData.getMarketPrices();
    bytes memory paraSwapData = mockData.getParaSwapData(vault);
    bytes[] memory swapData = new bytes[](1);
    swapData[0] = abi.encode(PROTOCOL.DEX, paraSwapData);
    vm.prank(keeper);
    PerpetualVault(vault).run(true, true, prices, swapData);

    uint256 executionFeeGasLimit = PerpetualVault(vault).getExecutionGasLimit(true);
    uint256 executionFee = executionFeeGasLimit * tx.gasprice;

    // bob's deposit after position is opened
    address bob = makeAddr("bob");
    deal(bob, executionFee);
    depositFixture(bob, 1e10);
    vm.prank(keeper);
    PerpetualVault(vault).runNextAction(prices, swapData);
    assertEq(uint8(PerpetualVault(vault).flow()), 1); // the flow still be DEPOSIT although bob's deposit is done

    // chris's deposit after bob's deposit
    address chris = makeAddr("chris");
    deal(chris, executionFee);
    IERC20 collateralToken = PerpetualVault(vault).collateralToken();
    vm.startPrank(chris);
    deal(address(collateralToken), chris, 1e10);
    
    collateralToken.approve(vault, 1e10);
    vm.expectRevert(Error.FlowInProgress.selector); // tx will be reverted due to the bob's deposit is not finalized the flow.
    PerpetualVault(vault).deposit{value: executionFee}(1e10);
    vm.stopPrank();
  }
```

## Recommendation
Within the PerpetualVault::runNextAction function, after the runSwap function is called, the flow should be finalized by calling the finalize function.
```diff
  function runNextAction(MarketPrices memory prices, bytes[] memory metadata) external nonReentrant gmxLock {
    _onlyKeeper();
    Action memory _nextAction = nextAction;
    delete nextAction;
    if (nextAction.selector == NextActionSelector.INCREASEACTION) {
      (bool isLong) = abi.decode(nextAction.data, (bool));

      if (isLongOneLeverage(isLong)) {
       _runSwap(metadata, true, prices);
       _finalize(hex'');
      } else {
    
    ...
  }
```
