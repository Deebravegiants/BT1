# [M] Revisited Calculation of Skim Amount

## Summary
Severity: Medium
Contest weight: 0.5933
Dataset id: 13425
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the Wombat protocol, the USDPlusAsset contract is added to support USD+ which is a rebasing token. The contract exposes a skim() function for the project owner to skim the extra reward in the same transaction with the payout. While reviewing the calculation of the skim amount that the owner can skim from the USD+ pool, we notice it does not properly take the pending fee and the tip bucket into consideration. To elaborate, we show below the code snippets of the skim()/_quoteSkimAmount() routines. As the name indicates, the skim() routine is used for the project owner to skim the USD+ from the pool. At the beginning, it calls the IPool(pool).mintFee() routine to distribute current collected fee in the pool (line 43). Then it calls the _quoteSkimAmount() routine which calculates the skim amount by subtracting the pool cash from the USD+ balance of the pool (line 55).
```solidity
function skim(address _to) external nonReentrant returns (uint256 amount) {
    require(hasRole(ROLE_USDPlusAdmin, msg.sender), "not authorized");
    IPool(pool).mintFee(underlyingToken);
    amount = _quoteSkimAmount();
    IERC20(underlyingToken).safeTransfer(_to, amount);
    emit Skim(amount, _to);
}
function _quoteSkimAmount() internal view returns (uint256 amount) {
    uint256 tokenBalance = IERC20(underlyingToken).balanceOf(address(this));
    uint256 cash_ = DSMath.fromWad(cash, underlyingTokenDecimals);
    if (tokenBalance < cash_) revert NotEnoughCash(tokenBalance, cash_);
    amount = tokenBalance - cash_;
}
```
However, it comes to our attention that the calculation of the skim amount does not take the pending fee and the tip bucket into consideration. Firstly, though it calls the IPool(pool).mintFee() routine to distribute the collected fee in advance, the current fee amount may not reach the mintFeeThreshold (line 988). In this case, the collected fee is still pending in the pool which needs to be subtracted from the skim amount. Secondly, the calculation does not subtract the tip bucket which is reserved from the fee as retention. As a result, the calculated skim amount may be much bigger than expectation and more USD+ is skimmed from the pool.
```solidity
function _mintFee(IAsset asset) internal {
    uint256 feeCollected = _feeCollected[asset];
    if (feeCollected == 0 || feeCollected < mintFeeThreshold) {
        // early return
        return;
    }
}
```

## Recommendation
Revisit the calculation of the skim amount to take the pending fee and the tip bucket into consideration.
