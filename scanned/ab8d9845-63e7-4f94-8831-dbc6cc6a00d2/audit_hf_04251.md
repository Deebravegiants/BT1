# [M] `confirmUnderwriter

## Summary
Severity: Medium
Contest weight: 0.6895
Dataset id: 21180
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
`getMinTimeBetweenWithdrawalQueues` is very important for `Pool`. If `getMinTimeBetweenWithdrawalQueues` is too small, `pendingQueues` will be overwritten too early, and when `Loan` pays off, it won't be able to find the corresponding `queues`.

So we will calculate `getMinTimeBetweenWithdrawalQueues` by `MaxDuration + _LOAN_BUFFER_TIME` to make sure it won't be overwritten too early.

```solidity
constructor(
    address _feeManager,
    address _offerHandler,
    uint256 _waitingTimeBetweenUpdates,
    OptimalIdleRange memory _optimalIdleRange,
    uint256 _maxTotalWithdrawalQueues,
    uint256 _reallocationBonus,
    ERC20 _asset,
    string memory _name,
    string memory _symbol
) ERC4626(_asset, _name, _symbol) LoanManager(tx.origin, _offerHandler, _waitingTimeBetweenUpdates) {
....
    getMinTimeBetweenWithdrawalQueues = (IPoolOfferHandler(_offerHandler).getMaxDuration() + _LOAN_BUFFER_TIME)
        .mulDivUp(1, _maxTotalWithdrawalQueues);
```

But switching the new `getUnderwriter/_offerHandler` doesn't recalculate the `getMinTimeBetweenWithdrawalQueues`.

```solidity
function confirmUnderwriter(address __underwriter) external onlyOwner {
    if (getPendingUnderwriterSetTime + UPDATE_WAITING_TIME > block.timestamp) {
        revert TooSoonError();
    }
    if (getPendingUnderwriter != __underwriter) {
        revert InvalidInputError();
    }

    getUnderwriter = __underwriter;
    getPendingUnderwriter = address(0);
    getPendingUnderwriterSetTime = type(uint256).max;

    emit UnderwriterSet(__underwriter);
}
```

This may break the expectation of `getMinTimeBetweenWithdrawalQueues`, and the new `getUnderwriter.getMaxDuration` is larger than the old one; which may cause `pendingQueues` to be overwritten prematurely.

## Recommendation
```solidity
contract Pool is ERC4626, InputChecker, IPool, IPoolWithWithdrawalQueues, LoanManager, ReentrancyGuard {
    uint256 public getMinTimeBetweenWithdrawalQueues;
...
    function confirmUnderwriter(address __underwriter) external override onlyOwner {
        super.confirmUnderwriter(__underwriter);
        uint256 newMinTime = (IPoolOfferHandler(__underwriter).getMaxDuration() + _LOAN_BUFFER_TIME)
         .mulDivUp(1, _maxTotalWithdrawalQueues);
        require(newMinTime >= getMinTimeBetweenWithdrawalQueues,"invalid");
        getMinTimeBetweenWithdrawalQueues = newMinTime;
    }
}
```
