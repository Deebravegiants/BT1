# [H] Tax-Evasion By Calling Transfer() Directly

## Summary
Severity: High
Contest weight: 0.7857
Dataset id: 11855
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Within the DarkCrypto protocol, Dark is an algorithmic token pegged to CRO and is designed to be used as a medium of exchange. The built-in stability mechanism in the protocol deterministically expands and contracts the DARK supply to maintain the DARK's peg to 1 CRO in the long run. At the same time, DARK is also used in the tax system where a tax is charged on selling DARKs. In the following, we analyze how the tax is applied in the implementation. Specifically, we show below the code snippet from the DarkCrypto::transferFrom() routine. This routine is called when the spender transfers DARK from the sender to the recipient. Inside this routine, a helper routine _transferWithTax() (line 208) is used to collect the tax.
```solidity
function transferFrom(
    address sender,
    address recipient,
    uint256 amount
) public override returns (bool) {
    uint256 currentTaxRate = 0;
    bool burnTax = false;
    if (autoCalculateTax) {
        uint256 currentDarkPrice = _getDarkPrice();
        currentTaxRate = _updateTaxRate(currentDarkPrice);
        if (currentDarkPrice < burnThreshold) burnTax = true;
    }
    if (currentTaxRate == 0 || excludedAddresses[sender]) {
        _transfer(sender, recipient, amount);
    } else {
        _transferWithTax(sender, recipient, amount, burnTax);
    }
    _approve(sender, _msgSender(), allowance(sender, _msgSender()).sub(amount, "ERC20: transfer amount exceeds allowance"));
    return true;
}
```
However, we notice an interesting tax-evasion issue that may prevent the tax-collection from properly functioning. Specifically, the tax-evasion issue comes from the fact that the tax-collection helper routine _transferWithTax() is only applied in the transferFrom() routine. If the sender calls the transfer() routine to directly transfer DARK to the spender and then let the spender to do another transfer() to transfer DARK to the recipient, the current tax-collection enforcement is bypassed.
```solidity
function transfer(address recipient, uint256 amount) public virtual override returns (bool) {
    _transfer(_msgSender(), recipient, amount);
    return true;
}
```

## Recommendation
Apply the tax-collection helper routine _transferWithTax() in the transfer() routine.
