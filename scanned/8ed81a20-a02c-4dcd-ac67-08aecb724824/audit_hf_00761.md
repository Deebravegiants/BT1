# [M] Swap functions are Reenterable

## Summary
Severity: Medium
Contest weight: 0.7643
Dataset id: 2375
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
[DiamondCutFacet.sol#L14-L22](https://github.com/code-423n4/2022-03-lifinance/blob/699c2305fcfb6fe8862b75b26d1d8a2f46a551e6/src/Facets/DiamondCutFacet.sol#L14-L22)  
[CBridgeFacet.sol#L92-L121](https://github.com/code-423n4/2022-03-lifinance/blob/699c2305fcfb6fe8862b75b26d1d8a2f46a551e6/src/Facets/CBridgeFacet.sol#L92-L121)  
[AnyswapFacet.sol#L74-L110](https://github.com/code-423n4/2022-03-lifinance/blob/699c2305fcfb6fe8862b75b26d1d8a2f46a551e6/src/Facets/AnyswapFacet.sol#L74-L110)  
[NXTPFacet.sol#L85-L102](https://github.com/code-423n4/2022-03-lifinance/blob/699c2305fcfb6fe8862b75b26d1d8a2f46a551e6/src/Facets/NXTPFacet.sol#L85-L102)  
[NXTPFacet.sol#L150-L171](https://github.com/code-423n4/2022-03-lifinance/blob/699c2305fcfb6fe8862b75b26d1d8a2f46a551e6/src/Facets/NXTPFacet.sol#L150-L171)  

There is a reenterancy vulnerability in functions which call `Swapper._executeSwap()` which would allow the attacker to change their `postSwapBalance`.

The functions following similar logic to that seen in `GenericSwapFacet.swapTokensGeneric()`.

```solidity
uint256 receivingAssetIdBalance = LibAsset.getOwnBalance(_lifiData.receivingAssetId);

// Swap
_executeSwaps(_lifiData, _swapData);

uint256 postSwapBalance = LibAsset.getOwnBalance(_lifiData.receivingAssetId) - receivingAssetIdBalance;

LibAsset.transferAsset(_lifiData.receivingAssetId, payable(msg.sender), postSwapBalance);
```

This logic records the balance before and after the `_executeSwaps()` function. The difference is then transferred to the `msg.sender`.

The issue occurs since it is possible for an attacker to reenter this function during `_executeSwaps()`, that is because execute swap makes numerous external calls, such as to the AMM, or to untrusted ERC20 token addresses.

If a function is called such as `WithdrawFacet.withdraw()` this will impact the calculations of `postSwapBalance` which will account for the funds transferred out during withdrawal. Furthermore, any functions which transfers funds into the contract will also be counted in the `postSwapBalance` calculations.

Vulnerable Functions:

  * `GenericSwapFacet.swapTokensGeneric()`
  * `CBridgeFacet.swapAndStartBridgeTokensViaCBridge()`
  * `AnyswapFacet.swapAndStartBridgeTokensViaAnyswap()`
  * `HopFacet.swapAndStartBridgeTokensViaHop()`
  * `NXTPFacet.swapAndStartBridgeTokensViaNXTP()`
  * `NXTPFacet.swapAndCompleteBridgeTokensViaNXTP()`

## Proof of Concept
`GenericSwapFacet.swapTokensGeneric()`

```solidity
function swapTokensGeneric(LiFiData memory _lifiData, LibSwap.SwapData[] calldata _swapData) public payable {
    uint256 receivingAssetIdBalance = LibAsset.getOwnBalance(_lifiData.receivingAssetId);

    // Swap
    _executeSwaps(_lifiData, _swapData);

    uint256 postSwapBalance = LibAsset.getOwnBalance(_lifiData.receivingAssetId) - receivingAssetIdBalance;

    LibAsset.transferAsset(_lifiData.receivingAssetId, payable(msg.sender), postSwapBalance);
}
```

`CBridgeFacet.swapAndStartBridgeTokensViaCBridge()`

```solidity
function swapAndStartBridgeTokensViaCBridge(
    LiFiData memory _lifiData,
    LibSwap.SwapData[] calldata _swapData,
    CBridgeData memory _cBridgeData
) public payable {
    if (_cBridgeData.token != address(0)) {
        uint256 _fromTokenBalance = LibAsset.getOwnBalance(_cBridgeData.token);

        // Swap
        _executeSwaps(_lifiData, _swapData);

        uint256 _postSwapBalance = LibAsset.getOwnBalance(_cBridgeData.token) - _fromTokenBalance;

        require(_postSwapBalance > 0, "ERR_INVALID_AMOUNT");

        _cBridgeData.amount = _postSwapBalance;
    } else {
        uint256 _fromBalance = address(this).balance;

        // Swap
        _executeSwaps(_lifiData, _swapData);

        uint256 _postSwapBalance = address(this).balance - _fromBalance;

        require(_postSwapBalance > 0, "ERR_INVALID_AMOUNT");

        _cBridgeData.amount = _postSwapBalance;
    }

    _startBridge(_cBridgeData);
}
```

`AnyswapFacet.swapAndStartBridgeTokensViaAnyswap()`

```solidity
function swapAndStartBridgeTokensViaAnyswap(
    LiFiData memory _lifiData,
    LibSwap.SwapData[] calldata _swapData,
    AnyswapData memory _anyswapData
) public payable {
    address underlyingToken = IAnyswapToken(_anyswapData.token).underlying();
    if (_anyswapData.token != address(0) && underlyingToken != IAnyswapRouter(_anyswapData.router).wNATIVE()) {
        if (underlyingToken == address(0)) {
            underlyingToken = _anyswapData.token;
        }

        uint256 _fromTokenBalance = LibAsset.getOwnBalance(underlyingToken);

        // Swap
        _executeSwaps(_lifiData, _swapData);

        uint256 _postSwapBalance = LibAsset.getOwnBalance(underlyingToken) - _fromTokenBalance;

        require(_postSwapBalance > 0, "ERR_INVALID_AMOUNT");

        _anyswapData.amount = _postSwapBalance;
    } else {
        uint256 _fromBalance = address(this).balance;

        // Swap
        _executeSwaps(_lifiData, _swapData);

        require(address(this).balance - _fromBalance >= _anyswapData.amount, "ERR_INVALID_AMOUNT");

        uint256 _postSwapBalance = address(this).balance - _fromBalance;

        require(_postSwapBalance > 0, "ERR_INVALID_AMOUNT");

        _anyswapData.amount = _postSwapBalance;
    }

    _startBridge(_anyswapData);
}
```

`HopFacet.swapAndStartBridgeTokensViaHop()`

```solidity
function swapAndStartBridgeTokensViaHop(
    LiFiData memory _lifiData,
    LibSwap.SwapData[] calldata _swapData,
    HopData memory _hopData
) public payable {
    address sendingAssetId = _bridge(_hopData.asset).token;

    uint256 _sendingAssetIdBalance = LibAsset.getOwnBalance(sendingAssetId);

    // Swap
    _executeSwaps(_lifiData, _swapData);

    uint256 _postSwapBalance = LibAsset.getOwnBalance(sendingAssetId) - _sendingAssetIdBalance;

    require(_postSwapBalance > 0, "ERR_INVALID_AMOUNT");

    _hopData.amount = _postSwapBalance;

    _startBridge(_hopData);
}
```

`NXTPFacet.swapAndStartBridgeTokensViaNXTP()`

```solidity
function swapAndStartBridgeTokensViaNXTP(
    LiFiData memory _lifiData,
    LibSwap.SwapData[] calldata _swapData,
    ITransactionManager.PrepareArgs memory _nxtpData
) public payable {
    address sendingAssetId = _nxtpData.invariantData.sendingAssetId;
    uint256 _sendingAssetIdBalance = LibAsset.getOwnBalance(sendingAssetId);

    // Swap
    _executeSwaps(_lifiData, _swapData);

    uint256 _postSwapBalance = LibAsset.getOwnBalance(sendingAssetId) - _sendingAssetIdBalance;

    require(_postSwapBalance > 0, "ERR_INVALID_AMOUNT");

    _nxtpData.amount = _postSwapBalance;

    _startBridge(_lifiData.transactionId, _nxtpData);
}
```

`NXTPFacet.swapAndCompleteBridgeTokensViaNXTP()`

```solidity
function swapAndCompleteBridgeTokensViaNXTP(
    LiFiData memory _lifiData,
    LibSwap.SwapData[] calldata _swapData,
    address finalAssetId,
    address receiver
) public payable {
    uint256 startingBalance = LibAsset.getOwnBalance(finalAssetId);

    // Swap
    _executeSwaps(_lifiData, _swapData);

    uint256 postSwapBalance = LibAsset.getOwnBalance(finalAssetId);

    uint256 finalBalance;

    if (postSwapBalance > startingBalance) {
        finalBalance = postSwapBalance - startingBalance;
        LibAsset.transferAsset(finalAssetId, payable(receiver), finalBalance);
    }

    emit LiFiTransferCompleted(_lifiData.transactionId, finalAssetId, receiver, finalBalance, block.timestamp);
}
```

## Recommendation
Consider adding a reentrancy guard over **every** function which may send or receive tokens. It may be easiest too add this guard over the `fallback()` function however that could prevent view functions from being called (since it would perform storage operations).

Ensure the same slot is used to store the reentrancy guard so all required functions are covered by a single guard.

> Bridge functions are vulnerable as well.

> Fixed in lifinance/lifi-contracts@703919f74d8b750e3bcf7a84bdcb4d742bc8d45a

> Sponsor confirmed with fix. While the reentrancy is valid there is no exploit, keeping this as Medium Risk.
