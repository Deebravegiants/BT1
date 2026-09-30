# [C] Synthetic tokens may be untransmutable

## Summary
Severity: Critical
Contest weight: 0.4937
Dataset id: 4213
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When creating a claim towards an Alchemist, the Transmuter uses the totalDebt for the Alchemist as a cap. Presumably, this is to ensure, in the multi-Alchemist scenario, that users don't over-burden one Alchemist with paying back more debt than that Alchemist has issued, essentially sanctioning other Alchemists. if (totalLocked + syntheticDepositAmount > IAlchemistV3(alchemist).totalDebt()) revert DepositCapReached(); However, this logic is flawed, since totalDebt tracks how leveraged the Alchemist is, not how many synthetic tokens are outstanding from it (and thus need to be accounted for). Specifically, repay() will reduce the totalDebt and send yield tokens to the Transmuter, hence making sure that the synthetic tokens it has issued are fully redeemable. But the totalDebt check will prevent redemptions in the Transmuter from being created if the synthetic tokens have been "paid off", due to the failure to account for the yield tokens sent to the Transmuter.

## Proof of Concept
In AlchemistV3.t.sol: function testLoanRepayAndRedemption() external { address user = address(0xbeef); uint256 ownedAmount = 100e18; uint256 depositAmount = ownedAmount / 2; // Deposit yield tokens to get a position vm.startPrank(user); SafeERC20.safeApprove(address(fakeYieldToken), address(alchemist), ownedAmount); alchemist.deposit(depositAmount, user, 0); uint256 nftId = AlchemistNFTHelper.getFirstTokenId(address(0xbeef), address(alchemistNFT)); // Mint synthetic tokens uint256 mintAmount = alchemist.getMaxBorrowable(nftId) / 2; alchemist.mint(nftId, mintAmount, user); // Repay the loan with yield tokens uint256 repayAmount = alchemist.convertDebtTokensToYield(mintAmount); alchemist.repay(repayAmount, nftId); // Create redemption in Transmuter SafeERC20.safeApprove(address(alToken), address(transmuterLogic), mintAmount); transmuterLogic.createRedemption(mintAmount); // [FAIL. Reason: DepositCapReached()] vm.stopPrank(); } This test imagines a scenario with a single user. They deposit yield tokens, takes out a loan, then repays their loan with their synthetic tokens. In this scenario, they then try to redeem them through the Transmuter. In reality, they may have sold the tokens in the open market, and some other user is looking to redeem them to e.g. close an arbitrage. However, the redemption cannot be created because the Alchemist has no outstanding debt and totalDebt == 0.

## Recommendation
If the protocol is designed to have only one Alchemist-Transmuter pair per synthetic token, then the check can be removed: all synthetic tokens should be redeemable through the one Transmuter. If the intention is to have multiple Transmuters, even just during migration from V2, then it is better keep track of the total outstanding tokens issued by the Alchemist in question, separately from totalDebt, and use that for the above check.
