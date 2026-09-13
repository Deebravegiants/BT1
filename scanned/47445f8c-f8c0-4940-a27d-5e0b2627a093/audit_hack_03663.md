# [M] Unsafe underlying token transfer in FeeBuyback

## Summary
Severity: Medium
Reporter: hyh
Source: https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/fee-buyback/FeeBuyback.sol#L68-L71
Type: audit-issue

## Details
# Unsafe underlying token transfer in FeeBuyback

## Summary

FeeBuyback's submit() and rescueERC20() use unsafe underlying token transfer. The functions will not revert on the transfer call failure and can be inaccessible for tokens not fully compliant with OZ's IERC20 (say, USDT). 

## Vulnerability Detail

One issue is that when a token do not revert, but instead return false this will go unnoticed in the current implementation with the corresponding downstream system's failures in the case of programmatic usage.

Another is that OZ IERC20 compliance is expected by using the unsafe version of transfer, while it is not always the case and such token will not be retrievable by the functions.

The latter means that submit() will be unavailable and remainder tokens will be frozen on the contract balance as rescueERC20() be also failing.

## Impact

In a situation when `transferFrom` failed silently own FeeBuyback balance will be used for the secondary swap, which is a kind of funds stealing.

Also, remainder funds from the FeeBuyback balance cannot be retrieved for tokens not compliant with OZ's IERC20.

Overall it's a fund loss and permanent fund freeze impact for a specific case of such tokens, so setting the severity to be medium.

## Code Snippet

FeeBuyback's submit() uses `transferFrom` without checking the result:

https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/fee-buyback/FeeBuyback.sol#L68-L71

```solidity
    //MATIC does not allow for approvals
    //ERC20s only
    if (token != MATIC) {
      IERC20(token).transferFrom(_safe, address(this), amount);
```

Plain `transfer` is used in rescueERC20():

https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/fee-buyback/FeeBuyback.sol#L84-L97

```solidity
  /**
  * @notice Sends ERC20 tokens trapped in contract to external address
  * @dev Only an owner is allowed to make this function call
  * @param account is the receiving address
  * @param externalToken is the token being sent
  * @param amount is the quantity being sent
  * @return boolean value indicating whether the operation succeeded.
  *
  * Emits a {Transfer} event.
  */
  function rescueERC20(address account, address externalToken, uint256 amount) public onlyExecutor() returns (bool) {
    IERC20(externalToken).transfer(account, amount);
    return true;
  }
```

In addition to ignoring the success value `transfer` returns, which leads to false success for the tokens that do not revert on a failure, it's assumed that the token fully complies with OZ's interface:

https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/fee-buyback/FeeBuyback.sol#L4-L5

```solidity
//imports
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
```

Some tokens to not adhere to IERC20 fully, not returning the state at all (mainnet USDT as an example), for them the transfer will be failing as not complying to the interface:

https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/token/ERC20/IERC20.sol#L34-L41

https://etherscan.io/address/0xdac17f958d2ee523a2206206994597c13d831ec7#code

## Tool used

Manual Review

## Recommendation

Consider using `safeTransfer` in both cases.
