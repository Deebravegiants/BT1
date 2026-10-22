# [H] Settlement can be called when auction period ends

## Summary
Severity: High
Contest weight: 0.8939
Dataset id: 20230
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The end of auction period is included in it across the logic, but settlePoolDebt() treats the last moment as if it is beyond the period.
In settlePoolDebt() SettlerActions.sol#L113 the end of period control do not revert at block.timestamp == kickTime + 72 hours, allowing to run the settlement at the very last moment of the period.
Pool manipulations become possible at this point of time as both quote and collateral removal operations (guarded by _revertIfAuctionClearable) and settlePoolDebt() are available at this point of time.
As an example, HPB depositor can monitor pool state and upon the calculation that their bucket can be used for bad debt settlement, atomically run removeQuoteToken() -> settlePoolDebt() -> addQuoteToken() at block.timestamp == kickTime + 72 hours, retaining yield generating HPB position, while funds of other depositors in nearby buckets are used for bad debt.
While the probability looks to be medium, catching the exact moment is cumbersome but achievable operation, the impact is one depositor profiting off others in a risk-free manner, so placing the overall severity to be medium.
settlePoolDebt() can be run at block.timestamp == kickTime + 72 hours:
external/SettlerActions.sol#L100-L113
```solidity
function settlePoolDebt(
    AuctionsState storage auctions_,
    mapping(uint256 => Bucket) storage buckets_,
    DepositsState storage deposits_,
    LoansState storage loans_,
    ReserveAuctionState storage reserveAuction_,
    PoolState calldata poolState_,
    SettleParams memory params_
) external returns (SettleResult memory result_) {
    uint256 kickTime = auctions_.liquidations[params_.borrower].kickTime;
    if (kickTime == 0) revert NoAuction();
    Borrower memory borrower = loans_.borrowers[params_.borrower];
    if ((block.timestamp - kickTime < 72 hours) && (borrower.collateral != 0)) revert AuctionNotClearable();
```
While AuctionNotCleared() is block.timestamp - kickTime > 72 hours, i.e. clearable auction is [0, 72 hours] period:
helpers/RevertsHelper.sol#L50-L57
```solidity
function _revertIfAuctionClearable(
    AuctionsState storage auctions_,
    LoansState storage loans_
) view {
    address head = auctions_.head;
    uint256 kickTime = auctions_.liquidations[head].kickTime;
    if (kickTime != 0) {
        if (block.timestamp - kickTime > 72 hours) revert AuctionNotCleared();
```
Reserves take also includes the last timestamp to the period, proceeding with take:
external/TakerActions.sol#L282-L291
```solidity
function takeReserves(
    ReserveAuctionState storage reserveAuction_,
    uint256 maxAmount_
) external returns (uint256 amount_, uint256 ajnaRequired_) {
    // revert if no amount to be taken
    if (maxAmount_ == 0) revert InvalidAmount();
    uint256 kicked = reserveAuction_.kicked;
    if (kicked != 0 && block.timestamp - kicked <= 72 hours) {
```

## Recommendation
Consider having settlePoolDebt() wait for the whole period to pass:
external/SettlerActions.sol#L100-L113
```solidity
function settlePoolDebt(
    ...
) external returns (SettleResult memory result_) {
    ...
    if ((block.timestamp - kickTime <= 72 hours) && (borrower.collateral != 0)) revert AuctionNotClearable();
```
