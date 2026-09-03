# [M] `withdraw` will revert if user had transferred shares

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-10-merit-circle
Published: 2022-10-14
Source: https://github.com/sherlock-audit/2022-10-merit-circle-judging/issues/122
Type: sherlock-finding

## Details
saian

medium

# `withdraw` will revert if user had transferred shares

## Summary

In function `withdraw` since shares burnt during withdraw, if a user transferred some shares to another account, the function will revert

## Impact

During withdraw the share amount value stored in `depositsOf` is burnt. But if a user had transferred some shares to another address, balance will be less than the share amount and the function will revert. And if the share amount cannot be transferred back to the user, some amount of depositTokens will be stuck in the contract.

## Code Snippet

https://github.com/Merit-Circle/merit-liquidity-mining/blob/ce5feaae19126079d309ac8dd9a81372648437f1/contracts/base/BasePool.sol#L90

```
    function _transfer(address _from, address _to, uint256 _value) internal virtual override {
		super._transfer(_from, _to, _value);
        _correctPointsForTransfer(_from, _to, _value);
	}

    function withdraw(uint256 _depositId, address _receiver) external {
        if (_depositId >= depositsOf[_msgSender()].length) {
            revert NonExistingDepositError();
        }
        Deposit memory userDeposit = depositsOf[_msgSender()][_depositId];
        if (block.timestamp < userDeposit.end) {
            revert TooSoonError();
        }

        // remove Deposit
        depositsOf[_msgSender()][_depositId] = depositsOf[_msgSender()][depositsOf[_msgSender()].length - 1];
        depositsOf[_msgSender()].pop();

        // burn pool shares
```

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-10-merit-circle-judging/issues/122_
