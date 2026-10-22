# [H] Several Business Logic Errors in VaultStrategy::prepareReturn()

## Summary
Severity: High
Contest weight: 0.6317
Dataset id: 12958
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
function prepareReturn(uint256 _debtOutstanding)
    internal
    override
    returns (
        uint256 _profit,
        uint256 _loss,
        uint256 _debtPayment
    )
{
    _profit = 0;
    _loss = 0; // for clarity
    _debtPayment = _debtOutstanding;
    uint256 total = estimatedTotalAssets();
    uint256 looseAssets = want.balanceOf(address(this));
    uint256 debt = vault.strategies(address(this)).totalDebt;
    if (total > debt) {
        // TODO: handle profit case
    } else {
        // serious loss should never happen but if it does, let's record it accurately
        _loss = debt.sub(total);
        uint256 amountToFree = _loss.add(_debtPayment);
        if (amountToFree > 0 && looseAssets < amountToFree) {
            // withdraw what we can
            withdraw(_withdrawSome(amountToFree.sub(looseAssets)));
            uint256 newLoose = want.balanceOf(address(this));
            // if we don't have enough money, adjust _debtOutstanding and only change profit needed
            if (newLoose < amountToFree) {
                if (_loss > newLoose) {
                    _loss = newLoose;
                    _debtPayment = 0;
                } else {
                    _debtPayment = Math.min(newLoose.sub(_loss), _debtPayment);
                }
            }
        }
    }
}
```
The first one is when total is smaller than debt, which means there is a loss and the routine needs to report it. However, there is a logic error with the calculated amountToFree, which should be equal to _debtPayment rather than amountToFree.sub(looseAssets). The second one is also in the case when total is smaller than debt and the routine needs to report a loss. The _loss should not be adjusted based on the relationship between newLoose and amountToFree. The third one is the computation of _debtPayment in a loss case. The _debtPayment should be newLoose regardless of whether newLoose is smaller than amountToFree or not.

## Recommendation
Correct the above logic error accordingly.
