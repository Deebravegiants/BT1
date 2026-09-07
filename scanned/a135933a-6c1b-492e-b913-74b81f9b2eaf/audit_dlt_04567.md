# [M] _withdraw() check the wrong variable

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-11-buffer
Published: 2022-11-22
Source: https://github.com/sherlock-audit/2022-11-buffer-judging/issues/117
Type: sherlock-finding

## Details
bin2chen

medium

# _withdraw() check the wrong variable

## Summary
in BufferBinaryPool#_withdraw() 
The real amount of transfers is "tokenXAmountToWithdraw", so we should use this variable to check if we have enough balance. But now we use "tokenXAmount"

## Vulnerability Detail

```solidity
    function _withdraw(uint256 tokenXAmount, address account)
        internal
        returns (uint256 burn)
    {
        require(
            tokenXAmount <= availableBalance(),
            "Pool: Not enough funds on the pool contract. Please lower the amount."
        );//**audit check tokenXAmount ***/
...

        uint256 tokenXAmountToWithdraw = maxUserTokenXWithdrawal < tokenXAmount
            ? maxUserTokenXWithdrawal
            : tokenXAmount;
...

        bool success = tokenX.transfer(account, tokenXAmountToWithdraw); //***audit but use tokenXAmountToWithdraw to transer ****/
        require(success, "Pool: The Withdrawal didn't go through");

```

## Impact

Restrictions are not allowed in special cases

## Code Snippet

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-11-buffer-judging/issues/117_
