# [H] Attackers will steal the reserve

## Summary
Severity: High
Contest weight: 0.6553
Dataset id: 2622
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
FlashSwapRouter::__swapDsforRa() is called as part of FlashSwapRouter::_swapRaforDs() whenever the reserve is sold and the resulting Ra is used to provide liquidity to the Vault by calling Vault::provideLiquidityWithFlashSwapFee(). However, if we follow the code, FlashSwapRouter::__swapDsforRa() calls FlashSwapRouter::__flashSwap(), which calls UniswapV2Pair::swap(). Then, the Uniswap pair calls uniswapV2Call(), which calls FlashSwapRouter::__afterFlashswapSell() and sends the Ra to the caller. Thus, the vault is providing a fee, but does not use the acquired funds to fund it, but the already existing Ra in the contract. The Ra meant for the liquidity fee is sent to the user calling FlashSwapRouter::_swapRaforDs(). In FlashSwapRouter.sol:124, FlashSwapRouter::__swapDsforRa() is called, which ultimately sends the Ra to the msg.sender. Internal pre-conditions None. External pre-conditions None. Attack Path 1. User calls swapRaforDs() and ends up receiving Ra which was intended for the Vault. Users can steal all reserve from the Vault.

## Proof of Concept
The following code snippets show how the Ra ends up in the caller, that is, the user that calls swapRaforDs().
```solidity
function __flashSwap(...) internal {
    bytes memory data = abi.encode(reserveId, dsId, buyDs, msg.sender, extraData);
    univ2Pair.swap(amount0out, amount1out, address(this), data);
}
function uniswapV2Call(address sender, uint256 amount0, uint256 amount1, bytes calldata data) external {
    (Id reserveId, uint256 dsId, bool buyDs, address caller, uint256 extraData) = abi.decode(data, (Id, uint256, bool, address, uint256));
    if (buyDs) {
    } else {
        uint256 amount = amount0 == 0 ? amount1 : amount0;
        __afterFlashswapSell(self, amount, reserveId, dsId, caller, extraData);
    }
}
function __afterFlashswapSell(...) internal {
    IERC20(ra).safeTransfer(caller, raAttributed);
}
```

## Recommendation
The FlashSwapRouter::__flashSwap() has to be modified to accept a caller argument, where it accepts either the msg.sender or owner(). In the flow of selling the reserve, it should send the Ra to the owner, which is the Vault.
