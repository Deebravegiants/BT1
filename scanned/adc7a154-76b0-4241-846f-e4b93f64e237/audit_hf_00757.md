# [M] SiloVault.sol :: Markets with assets that revert on zero approvals cannot be removed.

## Summary
Severity: Medium
Contest weight: 0.6333
Dataset id: 2347
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
To remove a market from the vault, the supply `cap` must be set to 0. However, when this happens, the market’s allowance to use tokens from the vault is also reset to 0. The issue arises because some tokens revert when attempting to approve a 0 value, preventing these markets from being removed from the vault.

## Proof of Concept
`submitMarketRemoval()` is implemented as follows.

```solidity
function submitMarketRemoval(IERC4626 _market) external virtual onlyCuratorRole {
    if (config[_market].removableAt != 0) revert ErrorsLib.AlreadyPending();
    if (config[_market].cap != 0) revert ErrorsLib.NonZeroCap();
    if (!config[_market].enabled) revert ErrorsLib.MarketNotEnabled(_market);
    if (pendingCap[_market].validAt != 0) revert ErrorsLib.PendingCap(_market);

    // Safe "unchecked" cast because timelock <= MAX_TIMELOCK.
    config[_market].removableAt = uint64(block.timestamp + timelock);

    emit EventsLib.SubmitMarketRemoval(_msgSender(), _market);
}
```

As you can see, removing a market requires setting the `cap` to 0 (the same applies to `updateWithdrawQueue()`). This is done by calling `submitCap()` with `_newSupplyCap` set to 0.

```solidity
function submitCap(IERC4626 _market, uint256 _newSupplyCap) external virtual onlyCuratorRole {
    if (_market.asset() != asset()) revert ErrorsLib.InconsistentAsset(_market);
    if (pendingCap[_market].validAt != 0) revert ErrorsLib.AlreadyPending();
    if (config[_market].removableAt != 0) revert ErrorsLib.PendingRemoval();
    uint256 supplyCap = config[_market].cap;
    if (_newSupplyCap == supplyCap) revert ErrorsLib.AlreadySet();

    if (_newSupplyCap < supplyCap) {
        _setCap(_market, SafeCast.toUint184(_newSupplyCap)); 
    } else {
        pendingCap[_market].update(SafeCast.toUint184(_newSupplyCap), timelock);

        emit EventsLib.SubmitCap(_msgSender(), _market, _newSupplyCap);
    }
}
```

In this case, the execution will enter the `if` section, which calls `_setCap()`, which invokes `setCap()` from the `SiloVaultActionsLib`.

```solidity
function setCap(
    IERC4626 _market,
    uint184 _supplyCap,
    address _asset,
    mapping(IERC4626 => MarketConfig) storage _config,
    mapping(IERC4626 => PendingUint192) storage _pendingCap,
    IERC4626[] storage _withdrawQueue
) external returns (bool updateTotalAssets) {
    MarketConfig storage marketConfig = _config[_market];
    uint256 approveValue;

    if (_supplyCap > 0) {
        if (!marketConfig.enabled) {
            _withdrawQueue.push(_market); 

            if (_withdrawQueue.length > ConstantsLib.MAX_QUEUE_LENGTH) revert ErrorsLib.MaxQueueLengthExceeded();

            marketConfig.enabled = true;

            // Take into account assets of the new market without applying a fee.
            updateTotalAssets = true;

            emit EventsLib.SetWithdrawQueue(msg.sender, _withdrawQueue);
        }

        marketConfig.removableAt = 0;
        // one time approval, so market can pull any amount from SiloVault in a future
        approveValue = type(uint256).max;
    }

    marketConfig.cap = _supplyCap;

    IERC20(_asset).forceApprove(address(_market), approveValue);

    emit EventsLib.SetCap(msg.sender, _market, _supplyCap);

    delete _pendingCap[_market];
}
```

As you can see, we do not enter the `if` block because `_supplyCap = 0`, which results in `approveValue = 0` (default value). This is expected since we want to clear the market’s allowance. However, some assets (such as [BNB](https://github.com/d-xo/weird-erc20?tab=readme-ov-file#revert-on-large-approvals--transfers)) revert when the approval value is set to `0`, causing `forceApprove()` to fail. 

As a result, the cap cannot be set to `0`, preventing the market from being removed. Furthermore, if the vault relies on markets with such assets and they cannot be removed, new ones cannot be added due to the `MAX_QUEUE_LENGTH` restriction.

In this case, [forceApprove()](https://github.com/OpenZeppelin/openzeppelin-contracts/blob/a31b4a438ad9b11368976140acd7da3ae27d717d/contracts/token/ERC20/utils/SafeERC20.sol#L101-L108) will not resolve the issue because it is only useful for tokens that revert the previous allowance is not set to zero. It does not address tokens that revert due to 0 approval amounts.

```solidity
function forceApprove(IERC20 token, address spender, uint256 value) internal {
    bytes memory approvalCall = abi.encodeCall(token.approve, (spender, value));

    if (!_callOptionalReturnBool(token, approvalCall)) {
        _callOptionalReturn(token, abi.encodeCall(token.approve, (spender, 0)));
        _callOptionalReturn(token, approvalCall);
    }
}
```

As you can see, if the initial approval call fails, the function first resets the allowance to zero and then attempts to approve the provided value again. However, since the value is 0, it will fail another time reverting the transaction. 

According to the contest specifications, tokens that **Revert on zero value approvals** are explicitly within scope.

## Recommendation
No recommendation
