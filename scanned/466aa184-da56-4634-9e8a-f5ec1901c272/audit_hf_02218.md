# [M] Potential Reentrancy Risks

## Summary
Severity: Medium
Contest weight: 0.4609
Dataset id: 12261
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
A common coding best practice in Solidity is the adherence of checks-effects-interactions principle. This principle is eﬀective in mitigating a serious attack vector known as re-entrancy. Via this particular attack vector, a malicious contract can be reentering a vulnerable contract in a nested manner. Speciﬁcally, it ﬁrst calls a function in the vulnerable contract, but before the ﬁrst instance of the function call is ﬁnished, second call can be arranged to re-enter the vulnerable contract by invoking functions that should only be executed once. This attack was part of several most prominent hacks in Ethereum history, including the DAO [16] exploit, and the recent Uniswap/Lendf.Me hack [15].

We notice that while checks-effects-interactions pattern is followed in most places, there is an occasion where this principle is violated. In the Holdefi contract, the repayBorrowInternal() function (see the code snippet below) is provided to repay the borrowed ETH or tokens and transfers any additional ETH amount sent back to the msg.sender. However, if the sender is a contract then the invocation of an external contract requires extra care in avoiding the above re-entrancy. Apparently, the interaction with the external contract (via line 1307) starts before eﬀecting update on internal states (beyond line 1309), hence violating the principle. While this ﬂow currently only refunds the extra amount back to the caller, there could be potential implications if this logic changes in future.

```solidity
/// @notice
/// Perform repay borrow operation
function repayBorrowInternal(address account, address market, address collateral, uint256 amount) internal whenNotPaused("repayBorrow") {
    MarketData memory borrowData;
    (borrowData.balance, borrowData.interest, borrowData.currentIndex) = getAccountBorrow(account, market, collateral);
    uint256 totalBorrowedBalance = borrowData.balance.add(borrowData.interest);
    require(totalBorrowedBalance != 0, "Total balance should not be zero");
    uint256 transferAmount = amount;
    if (transferAmount > totalBorrowedBalance) {
        transferAmount = totalBorrowedBalance;
    }
    if (market == ethAddress) {
        uint256 extra = amount.sub(transferAmount);
        transferFromHoldefi(msg.sender, ethAddress, extra);
    }
    if (market != ethAddress) {
        transferToHoldefi(address(this), market, transferAmount);
    }
    uint256 remaining = 0;
    if (transferAmount <= borrowData.interest) {
        borrowData.interest = borrowData.interest.sub(transferAmount);
    } else {
        remaining = transferAmount.sub(borrowData.interest);
        borrowData.interest = 0;
        borrowData.balance = borrowData.balance.sub(remaining);
    }
    borrows[account][collateral][market].balance = borrowData.balance;
    borrows[account][collateral][market].accumulatedInterest = borrowData.interest;
    borrows[account][collateral][market].lastInterestIndex = borrowData.currentIndex;
    collaterals[account][collateral].lastUpdateTime = block.timestamp;
    beforeChangeSupplyRate(market);
    marketAssets[market].totalBorrow = marketAssets[market].totalBorrow.sub(remaining);
    emit RepayBorrow(
        msg.sender,
        account,
        market,
        collateral,
        transferAmount,
        borrowData.balance,
        borrowData.interest,
        borrowData.currentIndex
    );
}
```

## Recommendation
Apply the checks-effects-interactions design pattern in all places or add the reentrancy guard modiﬁer for future-prooﬁng and extra-protection.
