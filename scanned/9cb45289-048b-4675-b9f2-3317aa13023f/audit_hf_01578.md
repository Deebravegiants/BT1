# [H] MJR-15 Using tokens with whitelist function

## Summary
Severity: High
Contest weight: 0.3063
Dataset id: 8468
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
At line: CreditManager.sol#L584-L593
The Gearbox protocol is assumed to use some tokens which have whitelist function (ex. USDC, USDT) like a collateral. If this token will be blocked off-chain the Liquidates credit account function member of the CreditManager contract (CreditManager.sol#L300) will not work correctly because the internal function _transferAssetsTo() (CreditManager.sol#L584-L591) returns incorrect return value totalValue.

## Proof of Concept
```solidity
function _transferAssetsTo(
    address creditAccount,
    address to,
    bool force
) internal returns (uint256 totalValue, uint256 totalWeightedValue) {
    totalValue = 0;
    totalWeightedValue = 0;
    uint256 tokenMask;
    uint256 enabledTokens = creditFilter.enabledTokens(creditAccount);
    for (uint256 i = 0; i < creditFilter.allowedTokensCount(); i++) {
        tokenMask = 1 << i;
        if (enabledTokens & tokenMask > 0) {
            (
                address token,
                uint256 amount,
                uint256 tv,
                uint256 tvw
            ) = creditFilter.getCreditAccountTokenById(creditAccount, i);
            if (amount > 1) {
                // The condition is met, but the transfer will not occur
                // for blocked account
                _safeTokenTransfer(
                    creditAccount,
                    token,
                    to,
                    amount.sub(1),
                    force
                );
                // In this case totalValue will not correct
                totalValue += tv;
                totalWeightedValue += tvw;
            }
        }
    }
}
```

## Recommendation
Use solution where totalValue will not increase in case of unsuccessful transaction.
