# [H] Token Overflow might result in system halt or loss of funds

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
#### Description
If a token overflows, some functionality such as `processProposal`, `cancelProposal` will break due to safeMath reverts. The overflow could happen because the supply of the token was artificially inflated to oblivion. 

This issue was pointed out by [Heiko Fisch](https://github.com/HeikoFisch) in Telegram chat. 

#### Examples
Any function using `internalTransfer()` can result in an overflow:


**contracts/Moloch.sol:L631-L634**
```solidity
function max(uint256 x, uint256 y) internal pure returns (uint256) {
    return x >= y ? x : y;
}

```

#### Recommendation
We recommend to allow overflow for broken or malicious tokens. This is to prevent system halt or loss of funds. It should be noted that in case an overflow occurs, the balance of the token will be incorrect for all token holders in the system.

`rageKick`, `rageQuit` were fixed by not using safeMath within the function code, however this fix is risky and not recommended, as there are other overflows in other functions that might still result in system halt or loss of funds. 

One suggestion is having a function named `unsafeInternalTransfer()` which does not use safeMath for the cases that overflow should be allowed. This mainly adds better readability to the code. 

**It is still a risky fix and a better solution should be planned.**
