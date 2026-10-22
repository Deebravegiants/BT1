# [M] Potential DoS in IndexRouter::mintSwap()

## Summary
Severity: Medium
Contest weight: 0.4596
Dataset id: 12737
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The Phuture protocol provides an IndexRouter contract, which is designed to be the main entry for interaction with protocol users. In particular, one entry routine, i.e., mintSwap(), accepts asset transfer-in, swaps and sends assets in certain proportions to vTokens, and mints the corresponding index tokens to represent the depositor's share. Our analysis shows that the current implementation has a potential denial-of-service issue. To elaborate, we show below the implementation of the related _mint() routine, which is invoked inside mintSwap(). We notice the requirement statement at the end of _mint(), i.e., require(IERC20(_inputToken).balanceOf(address(this)) == 0) (line 393). This enforcement is error-prone as a malicious actor may intentionally donate a tiny amount of inputToken, which renders the mintSwap() routine non-functional!

```solidity
function _mint(
    address _index,
    address _inputToken,
    uint _amountInInputToken,
    MintQuoteParams[] calldata _quotes
) internal {
    uint quotesCount = _quotes.length;
    IvTokenFactory vTokenFactory = IvTokenFactory(IIndex(_index).vTokenFactory());
    for (uint i; i < quotesCount; i++) {
        address asset = _quotes[i].asset;
        // if one of the assets is inputToken transfer directly to the vault
        if (asset == _inputToken) {
            IERC20(_inputToken).safeTransfer(
                vTokenFactory.createdVTokenOf(_inputToken),
                _quotes[i].buyAssetMinAmount
            );
            continue;
        }
        address swapTarget = _quotes[i].swapTarget;
        require(IAccessControl(registry).hasRole(EXCHANGE_TARGET_ROLE, swapTarget), "IndexRouter: INVALID_TARGET");
        _safeApprove(_inputToken, swapTarget, _amountInInputToken);
        // execute the swap with the quote for the asset
        _fillQuote(swapTarget, _quotes[i].assetQuote);
        uint assetBalanceAfter = IERC20(asset).balanceOf(address(this));
        require(assetBalanceAfter >= _quotes[i].buyAssetMinAmount, "IndexRouter: UNDERBOUGHT_ASSET");
        IERC20(asset).safeTransfer(vTokenFactory.createdVTokenOf(asset), assetBalanceAfter);
    }
    require(IERC20(_inputToken).balanceOf(address(this)) == 0, "IndexRouter: INVALID_INPUT_AMOUNT");
}
```

## Recommendation
Revise the above _mint() function to avoid the above denial-of-service situation.
