# [H] Incorrect Spend Allowance Management in CBI/JUKU

## Summary
Severity: High
Contest weight: 0.5983
Dataset id: 12334
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The JUKU platform has two standard ERC20-compliant tokens CBI and JUKU. Both tokens may charge a commission for each transfer. While examining the current commission-related logic, we notice the related spend allowance need to be adjusted. To elaborate, we show below the implementation of a standard ERC20 function, i.e., transferFrom(). As the name indicates, this function transfers the tokens from an owner s account to the receiver account, but only if the transaction initiator has suﬃcient allowance that has been previously approved by the owner to the transaction initiator. However, it comes to our attention that the spend allowance is adjusted based on the actual amount received by the receiver account (line 136)! The adjustment in fact needs to deduct the sent amount, which includes the feesAmount as well.
```solidity
function transferFrom(
    address from,
    address to,
    uint256 amount
) public override returns (bool) {
    if (taxFee == 0) {
        _spendAllowance(from, msg.sender, amount);
        _transfer(from, to, amount);
    } else {
        (uint256 sendAmount, uint256 feesAmount) = _checkFees(from, amount);
        _spendAllowance(from, msg.sender, sendAmount);
        _transfer(from, to, sendAmount);
        _transfer(from, feeCollector, feesAmount);
    }
    return true;
}
```

## Recommendation
Revise the above transferFrom() function to properly adjust the spending allowance after the transfer. The same issue is applicable to both CBI and JUKU token contracts.
