# [H] `Redeemer.sol#redeem

## Summary
Severity: High
Contest weight: 0.7852
Dataset id: 11506
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
function redeem(
    uint8 p,
    address u,
    uint256 m
) public returns (bool) {
    // Get the principal token that is being redeemed by the user
    address principal = IMarketPlace(marketPlace).markets(u, m, p);

    // Make sure we have the correct principal
    if (
        p != uint8(MarketPlace.Principals.Swivel) &&
        p != uint8(MarketPlace.Principals.Element) &&
        p != uint8(MarketPlace.Principals.Yield) &&
        p != uint8(MarketPlace.Principals.Notional)
    ) {
        revert Invalid('principal');
    }

    // The amount redeemed should be the balance of the principal token held by the Illuminate contract
    uint256 amount = IERC20(principal).balanceOf(lender);

    // Transfer the principal token from the lender contract to here
    Safe.transferFrom(IERC20(principal), lender, address(this), amount);

    if (p == uint8(MarketPlace.Principals.Swivel)) {
        // Redeems zc tokens to the sender's address
        ISwivel(swivelAddr).redeemZcToken(u, m, amount);
    } else if (p == uint8(MarketPlace.Principals.Element)) {
        // Redeems principal tokens from element
        IElementToken(principal).withdrawPrincipal(amount, marketPlace);
    } else if (p == uint8(MarketPlace.Principals.Yield)) {
        // Redeems prinicipal tokens from yield
        IYieldToken(principal).redeem(address(this), address(this), amount);
    } else if (p == uint8(MarketPlace.Principals.Notional)) {
        // Redeems the principal token from notional
        amount = INotional(principal).maxRedeem(address(this));
    }

    emit Redeem(p, u, m, amount);
    return true;
}
```

There are some protocols (eg Notional) that allows redeem before maturity, when doing so, they will actually make a market sell, usually means a discounted sale.

Since `redeem()` is a public function, anyone can call it before maturity, and force the whole protocol to sell it’s holdings at a discounted price, causing fund loss to the stake holders.

```solidity
function previewRedeem(uint256 shares) public view override returns (uint256 assets) {
    if (hasMatured()) {
        assets = convertToAssets(shares);
    } else {
        // If withdrawing non-matured assets, we sell them on the market (i.e. borrow)
        (uint16 currencyId, uint40 maturity) = getDecodedID();
        (assets, /* */, /* */, /* */) = NotionalV2.getPrincipalFromfCashBorrow(
            currencyId,
            shares,
            maturity,
            0,
            block.timestamp
        );
    }
}
```

## Recommendation
Consider only allow unauthenticated call after maturity.
