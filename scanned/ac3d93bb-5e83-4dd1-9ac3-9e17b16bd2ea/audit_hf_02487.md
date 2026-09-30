# [M] Incorrect Accounting in VotingEscrowV3:_receiveCrossChain()

## Summary
Severity: Medium
Contest weight: 0.4449
Dataset id: 13301
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
function _receiveCrossChain(
    address account,
    uint256 amount,
    uint256 unlockTime,
    uint256 fromChainID
) private {
    require(
        unlockTime + 1 weeks == _endOfWeek(unlockTime),
        "Unlock time must be end of a week"
    );
    LockedBalance memory lockedBalance = locked[account];
    if (lockedBalance.amount == 0) {
        require(
            !Address.isContract(account) || (addressWhitelist != address(0) && IAddressWhitelist(addressWhitelist).check(account)),
            "Smart contract depositors not allowed"
        );
    }
    uint256 newAmount = lockedBalance.amount.add(amount);
    uint256 newUnlockTime = lockedBalance.unlockTime.max(unlockTime).max(_endOfWeek(block.timestamp) + MIN_CROSS_CHAIN_RECEIVER_LOCK_PERIOD);
    _checkpointAndUpdateLock(
        lockedBalance.amount,
        lockedBalance.unlockTime,
        newAmount,
        newUnlockTime
    );
    locked[msg.sender].amount = newAmount;
    locked[msg.sender].unlockTime = newUnlockTime;
    // Withdraw CHESS from Anyswap pool
    address underlying = IAnyswapV6ERC20(anyswapChess).underlying();
    if (underlying == address(0)) {
        // anyswapChess is an AnyswapChessPool contract
        require(token == underlying);
        AnyswapChessPool(anyswapChess).withdrawUnderlying(amount);
    } else {
        // anyswapChess is an AnyswapChess contract
        IAnyswapV6ERC20(anyswapChess).mint(address(this), amount);
    }
    emit AmountIncreased(account, amount);
    if (newUnlockTime > lockedBalance.unlockTime) {
        emit UnlockTimeIncreased(msg.sender, newUnlockTime);
    }
    emit CrossChainReceived(msg.sender, fromChainID, amount, newUnlockTime);
}
```

## Recommendation
Properly update the given account's voting escrow information, instead of the calling user.
