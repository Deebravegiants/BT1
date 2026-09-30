# [M] Possible Tax Evasion For Certain Wallets

## Summary
Severity: Medium
Contest weight: 0.4595
Dataset id: 12107
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
function _handleTax() private instantTransfer {
    TaxToolkit.CollectedTaxes memory taxes = _calculateTaxesToSwap();
    if (!_isFueled) {
        _distributeTaxes(taxes);
        return;
    }
    uint256 outstanding = _loanManager.calculateOutstandingLoan(address(this));
    if (outstanding != 0) {
        /// @dev if the project owes fuel + interest.
        _pay(taxes.buy + taxes.sell + taxes.transfer, outstanding);
        return;
    }
    /// @dev "outstanding" could be 0 if it was paid off externally (either clawback or directly repaying the factory).
    _isFueled = false;
    _distributeTaxes(taxes);
}
```
A common coding best practice in Solidity is the adherence of checks-effects-interactions principle. This principle is effective in mitigating a serious attack vector known as re-entrancy. Via this particular attack vector, a malicious contract can be reentering a vulnerable contract in a nested manner. Specifically, it first calls a function in the vulnerable contract, but before the first instance of the function call is finished, second call can be arranged to re-enter the vulnerable contract by invoking functions that should only be executed once. This attack was part of several most prominent hacks in Ethereum history, including the DAO [13] exploit, and the Uniswap/Lendf.Me hack [12]. We notice there are occasions where the checks-effects-interactions principle is violated. Using the TaxToken as an example, the _handleTax() function (see the code snippet below) is provided to externally interact to transfer assets. However, the invocation of an external contract requires extra care in avoiding the above re-entrancy. For example, the interaction with the external contract (line 457) starts before effecting the update on internal state (in _instantTransfer), hence violating the principle. In this particular case, if the external contract has certain hidden logic that may be capable of launching re-entrancy to evade possible tax collection.

## Recommendation
Revisit the above routine to ensure the tax collection will not be evaded.
