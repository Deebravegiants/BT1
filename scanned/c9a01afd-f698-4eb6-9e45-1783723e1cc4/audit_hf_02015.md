# [H] Fees in the AutoCompoundingPodLp can be lost

## Summary
Severity: High
Contest weight: 0.7390
Dataset id: 11464
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the AutoCompoundingPodLp, when rewards are being processed, a protocol fee is taken:
```solidity
uint256 _pairedFee = (_pairedOut * protocolFee) / 1000;
if (_pairedFee > 0) {
    _protocolFees += _pairedFee;
    _pairedOut -= _pairedFee;
}
```
The fee tokens are not sent out of the contract, they are stored in the contract.
However, this means that when the rewarded token is the paired LP token, these fees will be autocompounded to the users, since the reward amount is calculated by checking the contract's balance:
```solidity
address _token = _i == _tokens.length ? pod.lpRewardsToken() : _tokens[_i];
uint256 _bal = IERC20(_token).balanceOf(address(this));
if (_bal == 0) {
    continue;
}
uint256 _newLp = _tokenToPodLp(_token, _bal, 0, _deadline);
_lpAmtOut += _newLp;
```

## Recommendation
It is recommended to transfer the protocol fees to a fee recipient address to prevent them from being later converted into staked LP tokens.
