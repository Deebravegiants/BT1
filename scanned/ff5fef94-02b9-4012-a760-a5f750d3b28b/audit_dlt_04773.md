# [M] In consistent modification of `_bridgeTxData` in `HardenedTopupProxy._processTopup()`.

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-10-mover
Published: 2022-10-28
Source: https://github.com/sherlock-audit/2022-10-mover-judging/issues/113
Type: sherlock-finding

## Details
hansfriese

medium

# In consistent modification of `_bridgeTxData` in `HardenedTopupProxy._processTopup()`.

## Summary
In consistent modification of `_bridgeTxData` in `HardenedTopupProxy._processTopup()`.

## Vulnerability Detail
The function `_processTopup()` is used to exchange any tokens to `cardTopupToken` and bridge to card L1.

When the input token is the same as the `cardTopupToken`, it doesn't use the `ExchangeProxy` and bridges directly [here](https://github.com/sherlock-audit/2022-10-mover/blob/main/cardtopup_contract/contracts/HardenedTopupProxy.sol#L315-L326) without changing `_bridgeTxData`.

```solidity
    if (_token == cardTopupToken) {
        // beneficiary is msg.sender (perform static check)
        IERC20Upgradeable(_token).safeTransferFrom(_beneficiary, address(this), _amount);

        uint256 feeAmount = _amount.mul(topupFee).div(1e18);

        // bridge from _beneficiary to card L1 relay
        _bridgeAssetDirect(_amount.sub(feeAmount), _bridgeType, _bridgeTxData);

        emit CardTopup(_beneficiary, _token, _amount, _amount.sub(feeAmount), _receiverHash);
        return;
    }
```

But when it works with other tokens, it modifies the `_bridgeTxData` after exchange [here](https://github.com/sherlock-audit/2022-10-mover/blob/main/cardtopup_contract/contracts/HardenedTopupProxy.sol#L345-L377).

```solidity
    // this is sanity check from the client if the swap misbehaves
    require(amountReceived >= _expectedMinimumReceived, "minimum swap amount not met");

    // fee is deducted in receiving token (USDC)
    if (topupFee != 0) {
        uint256 feeAmount = amountReceived.mul(topupFee).div(1e18);
```

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-10-mover-judging/issues/113_
