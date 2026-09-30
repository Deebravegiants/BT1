# [M] Improper Logic of StargateBorrow::borrowETH()

## Summary
Severity: Medium
Contest weight: 0.4590
Dataset id: 12866
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the Radiant V2 protocol, the StargateBorrow contract is one of the main entries for interaction with users, which allows the user to borrow assets from the lending pool on the source chain and bridge the borrowed assets to the destination chain via Stargate. In particular, the internal borrowETH() routine (called inside borrow()) is designed to borrow ETH and bridge the borrowed ETH to the user specified destination chain. While examining its logic, we observe its current implementation needs to be improved. To elaborate, we show below the related code snippet of the StargateBorrow contract. Inside the borrowETH() routine, the lendingPool.borrow() is called (line 189) to borrow WETH from the lending pool. And then the borrowed WETH is unwrapped back to ETH (line 196). The unwrapped ETH minus the bridge fee (line 199) will be bridged to the destination chain via the call to router.swap() (line 200). However, it ignores the fact that the router.swap() cannot support native token (i.e., ETH) cross-chain transfer, which will result in getting the transaction always reverted.

```solidity
function borrow(
    address asset,
    uint256 amount,
    uint256 interestRateMode,
    uint16 dstChainId
) external payable {
    if (address(asset) == ETH_ADDRESS) {
        borrowETH(amount, interestRateMode, dstChainId);
    } else {
        // Handle other assets
    }
}

function borrowETH(
    uint256 amount,
    uint256 interestRateMode,
    uint16 dstChainId
) internal {
    lendingPool.borrow(
        address(WETH),
        amount,
        interestRateMode,
        address(this),
        msg.sender,
        0
    );
    WETH.withdraw(amount);
    uint256 feeAmount = getXChainBorrowFeeAmount(amount);
    _safeTransferETH(daoTreasury, feeAmount);
    amount = amount.sub(feeAmount);
    router.swap{value: msg.value}(
        dstChainId, // dest chain id
        PoolIdETH, // src chain pool id
        PoolIdETH, // dst chain pool id
        msg.sender, // receive address
        amount, // transfer amount
        amount.mul(99).div(100), // max slippage: 1%
        IStargateRouter.lzTxObj(0, 0, "0x"),
        abi.encodePacked(msg.sender),
        bytes("")
    );
}
```

## Recommendation
Wrap ETH to SGETH before the call to router.swap().
