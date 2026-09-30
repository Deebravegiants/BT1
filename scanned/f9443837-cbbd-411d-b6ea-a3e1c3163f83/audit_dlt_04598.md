# [M] There is no delay in executorship's propose/accept logic

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-11-telcoin
Published: 2022-11-22
Source: https://github.com/sherlock-audit/2022-11-telcoin-judging/issues/89
Type: sherlock-finding

## Details
hyh

medium

# There is no delay in executorship's propose/accept logic

## Summary

TieredOwnership implementation of the two step role transfer process lacks a major detail: there is no time delay in-between the nomination of a new executor and the actual promotion to the role.

## Vulnerability Detail

Without a delay users will not be able to react to the change of the executor role holder.

Two-step process is crucial not only by being mutual, i.e. requiring both current and new executors to act, but by the introduction of a period of time between proposing a new actor and implementing the change, so all the users of the protocol be able to act on it, if needed.

## Impact

FeeBuyback users will not be able to react to the Executor role holder change, which can lead to the loss of funds the FeeBuyback contract holds as the role has full access to its balance.

Setting the severity to medium due to prerequisites: a new malicious executor needs to trick the old prudent one to nominate or to use a vulnerability to run the nomination with old executor account.

## Code Snippet

nominateExecutor() and acceptExecutorship() can be run instantly by the collided old and new executors:

https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/fee-buyback/TieredOwnership.sol#L59-L80

```solidity
    /**
     * @notice nominates address as new executor
     * @param newExecutor address is the new address being given executorship
     *
     * Emits a {ExecutorNominated} event.
     */
    function nominateExecutor(address newExecutor) external onlyExecutor() {
        _nominatedExecutor = newExecutor;
        emit ExecutorNominated(_nominatedExecutor);
    }

    /**
     * @notice promotes nominated executor to executor
     *
     * Emits a {ExecutorChanged} event.
     */
    function acceptExecutorship() external {
        require(_msgSender() == nominatedExecutor(), "TieredOwnership: You must be nominated before you can accept executorship");
        emit ExecutorChanged(executor(), nominatedExecutor());
        _executor = nominatedExecutor();
        _nominatedExecutor = address(0);
    }
```

This will leave no time for the users to react on the change, which invalidates the base purpose of the two-step procedure.

TieredOwnership is being used in FeeBuyback role management:

https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/fee-buyback/FeeBuyback.sol#L10-L15

```solidity
/**
 * @title FeeBuyback
 * @author Amir Shirif, Telcoin, LLC.
 * @notice Helps facilitate a secondary swap, if required, to allow the referrer of a user to receive a fraction of the generated transaction fee, based on the stake of the referrer.
 */
contract FeeBuyback is IFeeBuyback, TieredOwnership {
```

Executor can obtain any remainder tokens from the contract:

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


## Tool used

Manual Review

## Recommendation

Consider introducing a delay between nominating and accepting of the new executor, for example:

https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/fee-buyback/TieredOwnership.sol#L59-L80

```solidity
    /**
     * @notice nominates address as new executor
     * @param newExecutor address is the new address being given executorship
     *
     * Emits a {ExecutorNominated} event.
     */
    function nominateExecutor(address newExecutor) external onlyExecutor() {
+       _executorNominationTime = blocks.timestamp;        
        _nominatedExecutor = newExecutor;
        emit ExecutorNominated(_nominatedExecutor);
    }

    /**
     * @notice promotes nominated executor to executor
     *
     * Emits a {ExecutorChanged} event.
     */
    function acceptExecutorship() external {
+       require(blocks.timestamp > _executorNominationTime + 7 days, "TieredOwnership: Too early");
        require(_msgSender() == nominatedExecutor(), "TieredOwnership: You must be nominated before you can accept executorship");
        emit ExecutorChanged(executor(), nominatedExecutor());
        _executor = nominatedExecutor();
        _nominatedExecutor = address(0);
    }
```
