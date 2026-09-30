# [H] FlashSwapRouter::emptyReserve()

## Summary
Severity: High
Contest weight: 0.9152
Dataset id: 2615
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The protocol deposits RA and CT tokens to an AMM pair, from fees or when users call the depositLv() function. The CT and DS tokens issued by the protocol have an expiration, after the first DS and CT tokens for a pair have been issued and expired, each next time the protocol tries to issue new DS and CT tokens for an existing pair of RA and PA tokens via calling the issueNewDs() function, the VaultLib::onNewIssuance() function will be called. The VaultLib::onNewIssuance() function will then call the VaultLib::_liquidatedLp() function, which internally calls the FlashSwapRouter::emptyReserve() function which will empty the whole reserve, and then return 0.

```solidity
function emptyReserve(ReserveState storage self, uint256 dsId, address to) internal returns (uint256 reserve) {
    reserve = emptyReservePartial(self, dsId, self.ds[dsId].reserve, to);
}

function emptyReservePartial(ReserveState storage self, uint256 dsId, uint256 amount, address to) internal returns (uint256 reserve) {
    self.ds[dsId].ds.transfer(to, amount);
    self.ds[dsId].reserve -= amount;
    reserve = self.ds[dsId].reserve;
}
```

When we go back to the VaultLib::_liquidatedLp() function:

```solidity
function _liquidatedLp(
    State storage self,
    uint256 dsId,
    IUniswapV2Router02 ammRouter,
    IDsFlashSwapCore flashSwapRouter
) internal {
    // the following things should happen here(taken directly from the whitepaper):
    // 1. The AMM LP is redeemed to receive CT + RA
    // 2. Any excess DS in the LV is paired with CT to redeem RA
    // 3. The excess CT is used to claim RA + PA in the PSM
    // 4. End state: Only RA + redeemed PA remains
    uint256 reservedDs = flashSwapRouter.emptyReserve(self.info.toId(), dsId);
    uint256 redeemAmount = reservedDs >= ctAmm ? ctAmm : reservedDs;
    PsmLibrary.lvRedeemRaWithCtDs(self, redeemAmount, dsId);
    // if the reserved DS is more than the CT that's available from liquidating the AMM LP
    // then there's no CT we can use to effectively redeem RA + PA from the PSM
    uint256 ctAttributedToPa = reservedDs >= ctAmm ? 0 : ctAmm - reservedDs;
    uint256 psmPa;
    uint256 psmRa;
    if (ctAttributedToPa != 0) {
        (psmPa, psmRa) = PsmLibrary.lvRedeemRaPaWithCt(self, ctAttributedToPa, dsId);
    }
    psmRa += redeemAmount;
    self.vault.pool.reserve(self.vault.lv.totalIssued(), raAmm + psmRa, psmPa);
}
```

be paired and redeemed for RA, however since the FlashSwapRouter::emptyReserve() function will always return 0, so the PsmLib::lvRedeemRaWithCtDs() function will always redeem 0 RA tokens and not burn the CT and DS tokens. As we can see from the above code snippet we will go directly to PsmLib::lvRedeemRaPaWithCt() function, which will try to redeem RA + PA tokens, with all of the CT tokens that were returned from the UniV2 pair when the LP tokens of the protocol were liquidated.

The second case where a problem occurs is when a user tries to redeem his LV tokens by calling the redeemEarlyLv() function which internally calls the VaultLib::redeemEarly() function and after a couple of other internal calls the VaultLib::_redeemCtDsAndSellExcessCt() function is called where the FlashSwapRouter::emptyReservePartial() function is called:

```solidity
function _redeemCtDsAndSellExcessCt(
    State storage self,
    uint256 dsId,
    IUniswapV2Router02 ammRouter,
    IDsFlashSwapCore flashSwapRouter,
    uint256 ammCtBalance
) internal returns (uint256 ra) {
    uint256 reservedDs = flashSwapRouter.getLvReserve(self.info.toId(), dsId);
    uint256 redeemAmount = reservedDs >= ammCtBalance ? ammCtBalance : reservedDs;
    reservedDs = flashSwapRouter.emptyReservePartial(self.info.toId(), dsId, redeemAmount);
    ra += redeemAmount;
    PsmLibrary.lvRedeemRaWithCtDs(self, redeemAmount, dsId);
    uint256 ctSellAmount = reservedDs >= ammCtBalance ? 0 : ammCtBalance - reservedDs;
    DepegSwap storage ds = self.ds[dsId];
    address[] memory path = new address[](2);
    path[0] = ds.ct;
    path[1] = self.info.pair1;
    ERC20(ds.ct).approve(address(ammRouter), ctSellAmount);
    if (ctSellAmount != 0) {
        // 100% tolerance, to ensure this not fail
        ra += ammRouter.swapExactTokensForTokens(ctSellAmount, 0, path, address(this), block.timestamp)[1];
    }
}
```

When the last LV tokens are being redeemed the reservedDs will be equal or very close to ammCtBalance, and when the FlashSwapRouter::emptyReservePartial() function is called, it will return the DS reserve after the redeemAmount has been subtracted, which will be either 0, or much less than redeemAmount. For this example consider it is 0. When the ctSellAmount is calculated it will be much bigger than the actual reserves of CT token in the contract, and when the function tries to transfer the CT tokens to the AMM in order to swap them for RA tokens, the call will revert, and the user redeeming his LV token won't be able to redeem it and receive RA tokens back, thus locking funds in the contract.

The root cause is that the FlashSwapRouter::emptyReserve() and FlashSwapROuter::emptyReservePartial() functions returns the reserve that is left after the redeemAmount has been subtracted.

Internal pre-conditions  
1. Users mint LV tokens via the depositLv() function  
2. There are a couple of LV tokens that haven't been redeemed yet, and a user decides to redeem them by calling the VaultLib::redeemEarly() function  

External pre-conditions  
Attack Path  
When it comes to FlashSwapRouter::emptyReserve(), instead of the excess DS in the LV being paired with CT to redeem RA, all of the CT returned from the liquidation of LP will be used to claim RA + PA in the PSM, this is contrary of what is expected from the VaultLib::_liquidatedLp() function claiming much more PA tokens than it should, and distributing them to LV holders. In the case of FlashSwapROuter::emptyReservePartial(), the last users to withdraw won't be able to do so. The last user that tries to redeem his LV tokens won't be able to do so, and he won't receive his RA tokens back, locking the RA tokens in the contract.

## Proof of Concept
Gist  
orTests.t.sol contract:  
```solidity
function test_IncorrectEmptyReserveReturnedValue() public {
    vm.startPrank(alice);
    WETH.mint(alice, 10e18);
    WETH.approve(address(moduleCore), type(uint256).max);
    moduleCore.depositLv(id, 10e18);
    Asset(lvAddress).approve(address(moduleCore), type(uint256).max);
    vm.expectRevert(bytes("TransferHelper::transferFrom: transferFrom failed"));
    moduleCore.redeemEarlyLv(id, alice, 10e18);
    vm.stopPrank();
}
```
To run the test use: forgetest-vvv--mttest_IncorrectEmptyReserveReturnedValue

## Recommendation
A lot of things have to be considered when fixing this problems, simply returning the amount that was redeemed may introduce other problems. Returning the amount that was redeemed seems to be okay when it comes to the FlashSwapRouter::emptyReserve() function.
