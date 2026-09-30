# [H] Wrong _prevRatios index could be

## Summary
Severity: High
Contest weight: 0.7985
Dataset id: 10052
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
When addLiquidity is called and initial liquidity has already been provided,
the caller can skip providing one of the listed tokens by setting the
corresponding value in amounts_ to 0. If the amount provided is 0, the
function will skip updating the token and pool virtual balance product and
sum, as well as skip storing _prevRatios.
function addLiquidity
(uint256[] calldata amounts_, uint256 minLpAmount_, address receiver_)
external
nonReentrant
returns (uint256)
uint256 _numTokens = numTokens;
if (amounts_.length != _numTokens) revert Pool__InvalidParams();
// ...
// update rates
(_virtualBalanceProd, _virtualBalanceSum) = _updateRates
(_tokens, _virtualBalanceProd, _virtualBalanceSum);
uint256 _prevSupply = supply;
uint256 _virtualBalanceProdFinal = _virtualBalanceProd;
uint256 _virtualBalanceSumFinal = _virtualBalanceSum;
uint256 _prevVirtualBalanceSum = _virtualBalanceSum;
uint256[] memory _prevRatios = new uint256[](_numTokens);
uint256 _virtualBalance;
for (uint256 t = 0; t < MAX_NUM_TOKENS; t++) {
    if (t == _numTokens) break;
    uint256 __amount = amounts_[t];
    if (__amount == 0) {
        if (!(_prevSupply > 0)) {
            revert Pool__InitialDepositAmountMustBeNonZero();
        }
        continue;
    }
    // update stored virtual balance
    (_prevVirtualBalance, _rate, _packedWeight) = _unpackVirtualBalance
    (packedVirtualBalances[t]);
    uint256 _changeInVirtualBalance = (__amount * _rate) / PRECISION;
    _virtualBalance = _prevVirtualBalance + _changeInVirtualBalance;
    packedVirtualBalances[t] = _packVirtualBalance
    (_virtualBalance, _rate, _packedWeight);
    if (_prevSupply > 0) {
        _prevRatios[t] =
        (_prevVirtualBalance * PRECISION) / _prevVirtualBalanceSum;
        uint256 _weightTimesN = _unpackWeightTimesN
        (_packedWeight, _numTokens);
        // update product and sum of virtual balances
        _virtualBalanceProdFinal = (
            _virtualBalanceProdFinal
            * _powUp((
            ) / _virtualBalance, _weightTimesN
            ) / PRECISION;
        // the `D^n` factor will be updated in `_calculateSupply()`
        _virtualBalanceSumFinal += _changeInVirtualBalance;
        // remove fees from balance and recalculate sum and product
        uint256 _fee = (
            (_changeInVirtualBalance -
            (_prevVirtualBalance * _lowest) / PRECISION) * (swapFeeRate / 2)
        ) / PRECISION;
        _virtualBalanceProd = (
            _virtualBalanceProd
            * _powUp((_prevVirtualBalance * PRECISION) /
            (_virtualBalance - _fee), _weightTimesN)
        ) / PRECISION;
        _virtualBalanceSum += _changeInVirtualBalance - _fee;
        SafeTransferLib.safeTransferFrom(tokens[t], msg.sender, address
        (this), __amount);
// ...
However, when checking if ratios change within a valid band, it will provide
prevRatios at the wrong index.
// ...
uint256 _supply = _prevSupply;
if (_prevSupply == 0) {
    // initial deposit, calculate necessary variables
    _virtualBalanceProd,
    _virtualBalanceSum
    ) = _calculateVirtualBalanceProdSum(
    if (!(_virtualBalanceProd > 0)) revert Pool__AmountsMustBeNonZero();
    _supply = _virtualBalanceSum;
} else {
    // check bands
    uint256 _j = 0;
    for (uint256 t = 0; t < MAX_NUM_TOKENS; t++) {
        if (t == _numTokens) break;
        if (amounts_[t] == 0) continue;
        (_virtualBalance, _rate, _packedWeight) = _unpackVirtualBalance
        (packedVirtualBalances[t]);
        _checkBands(_prevRatios[_j],
        (_virtualBalance * PRECISION) / _virtualBalanceSumFinal, _packedWeight);
        _j = FixedPointMathLib.rawAdd(_j, 1);
// ...
Consider a scenario where there are 3 tokens (token index 0, index 1, and
index 2).
when addLiquidity is called, skipping index 1 token, with amounts_ at index
1 set to 0.
When _checkBands is called for the token at index 2, it will provide
_prevRatios at index _j equal to 1 (since token index 1 skipped at not
incrementing _j). This is incorrect because when storing _prevRatios, the
actual index (t) is used regardless of whether there is a skipped token or not.
This could cause the valid addLiquidity operation to revert due to using
_prevRatios at the wrong index.
```

## Recommendation
```solidity
Use t index instead of _j:
// ...
uint256 _supply = _prevSupply;
if (_prevSupply == 0) {
    // initial deposit, calculate necessary variables
    _virtualBalanceProd,
    _virtualBalanceSum
    ) = _calculateVirtualBalanceProdSum(
    if (!(_virtualBalanceProd > 0)) revert Pool__AmountsMustBeNonZero();
    _supply = _virtualBalanceSum;
} else {
    // check bands
    // uint256 _j = 0;
    for (uint256 t = 0; t < MAX_NUM_TOKENS; t++) {
        if (t == _numTokens) break;
        if (amounts_[t] == 0) continue;
        (_virtualBalance, _rate, _packedWeight) = _unpackVirtualBalance
        (packedVirtualBalances[t]);
        // _checkBands(_prevRatios[_j],
        // (_virtualBalance * PRECISION) / _virtualBalanceSumFinal, _packedWeight);
        _checkBands(_prevRatios[t],
        (_virtualBalance * PRECISION) / _virtualBalanceSumFinal, _packedWeight);
        // _j = FixedPointMathLib.rawAdd(_j, 1);
// ...
```
