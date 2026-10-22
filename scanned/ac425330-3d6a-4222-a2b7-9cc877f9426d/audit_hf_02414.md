# [H] Potential DoS With Vault::withdraw()

## Summary
Severity: High
Contest weight: 0.7857
Dataset id: 12981
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The SatoshiSwap Vault Module allows users to deposit assets into (and withdraw from) the Vault. When a user intends to withdraw, the withdraw() routine will trigger the related Strategy's withdraw(), which handles the actual withdrawal from the MarginPool. To elaborate, we show below the related code snippet.
```solidity
function withdraw(uint256 _amountNeeded) external returns (uint256 _loss) {
    require(msg.sender == address(vault), "!vault");
    // Liquidate as much as possible to want, up to _amountNeeded
    uint256 amountFreed;
    (amountFreed, _loss) = liquidatePosition(_amountNeeded);
    // Send it directly back (NOTE: Using msg.sender saves some gas here)
    want.safeTransfer(msg.sender, amountFreed);
    // NOTE: Reinvest anything leftover on next tend / harvest
}
```
```solidity
function liquidatePosition(uint256 _amountNeeded) internal override returns (uint256 _amountFreed, uint256 _loss) {
    if (emergencyExit) {
        // Liquidate everything
        _amountFreed = IGenericMarginPool(pool).nav();
        _loss = 0;
    } else {
        uint256 _balance = want.balanceOf(address(this));
        if (_balance >= _amountNeeded) {
            // if we don't set reserve here withdrawer will be sent our full balance
            return (_amountNeeded, 0);
        } else {
            uint256 received = _withdrawSome(_amountNeeded.sub(_balance)).add(
                _balance);
            return (received, 0);
        }
    }
}
```
```solidity
function _withdrawSome(uint256 _amount) internal returns (uint256) {
    _amount = Math.min(_amount, IGenericMarginPool(pool).nav());
    // dont withdraw dust
    if (_amount < withdrawalThreshold) {
        return 0;
    }
    return IGenericMarginPool(pool).withdraw(_amount);
}
```
When analyzing these routines, we notice the liquidatePosition() routine will call the _withdrawSome() routine, which performs the withdraw from the MarginPool. However, if all the funds in the MarginPool are borrowed out to open the positions, there is nothing available from Vault (because the liquidatePosition() routine does not perform a real liquidation). What's more, liquidatePosition() never reports a lost on a non-emergency exit so the Vault could not be informed of this situation and handle the debtRatio accordingly.

## Recommendation
Properly handle the case when most of the funds are borrowed out from the MarginPool.
