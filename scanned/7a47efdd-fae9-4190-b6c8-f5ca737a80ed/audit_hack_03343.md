# [M] [Tomo-M2] Use safe version ERC20 transfer

## Summary
Severity: Medium
Reporter: Tomo
Source: https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/SmartRoute/DODORouteProxy.sol#L418-L424
Type: audit-issue

## Details
# [Tomo-M2] Use safe version ERC20 transfer

## Summary

Use the safe version ERC20 transfer

## Vulnerability Detail

Some tokens (like USDT) don't correctly implement the EIP20 standard and their `transfer`/`transferFrom` function return `void` instead of a success boolean. Calling these functions with the correct EIP20 function signatures will always revert.

The `ERC20.transfer()` and `ERC20.transferFrom()` functions return a boolean value indicating success. This parameter needs to be checked for success. Some tokens do **not** revert if the transfer failed but return `false` instead.

Also, this project assumes any ERC20 so this issue does matter for this project.

``` solidity
ERC20: any
ERC721: none
```

Ref: [https://github.com/sherlock-audit/2022-11-dodo-Tomosuke0930#on-chain-context](https://github.com/sherlock-audit/2022-11-dodo-Tomosuke0930#on-chain-context)

## Impact

Tokens that don't actually perform the transfer and return false are still counted as a correct transfer and tokens that don't correctly implement the latest EIP20 spec, like USDT, will be unusable in the protocol as they revert the transaction because of the missing return value.

## Code Snippet

[https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/SmartRoute/DODORouteProxy.sol#L418-L424](https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/SmartRoute/DODORouteProxy.sol#L418-L424)

``` solidity
if (curPoolInfo.poolEdition == 1) {
    //For using transferFrom pool (like dodoV1, Curve), pool call transferFrom function to get tokens from adapter
    IERC20(midToken[i]).transfer(curPoolInfo.adapter, curAmount);
} else {
    //For using transfer pool (like dodoV2), pool determine swapAmount through balanceOf(Token) - reserve
    IERC20(midToken[i]).transfer(curPoolInfo.pool, curAmount);
}
```

## Tool used

Manual Review

## Recommendation

I recommend using OpenZeppelin’s `SafeERC20` versions with the `safeTransfer`
 and `safeTransferFrom` functions that handle the return value check as well as non-standard-compliant tokens.

[https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/token/ERC20/utils/SafeERC20.sol](https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/token/ERC20/utils/SafeERC20.sol)
