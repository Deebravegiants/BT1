# [M] The functions about permit won't work and al-

## Summary
Severity: Medium
Contest weight: 0.4638
Dataset id: 22479
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The functions about permit won't work and always revert JalaRouter02.sol has functions (removeLiquidityWithPermit/removeLiquidityETHWithPermit/removeLiquidityETHWithPermitSupportingFeeOnTransferTokens) about permit. These functions will call permit function in JalaPair.sol. JalaPair is inherited from JalaERC20. Although JalaERC20 is out of scope. But both JalaPair and JalaERC20 have no permit functions. So when you call removeLiquidityWithPermit/removeLiquidityETHWithPermit/removeLiquidityETHWithPermitSupportingFeeOnTransferTokens it will always revert. We can't remove liquidity by using permit.

## Proof of Concept
```solidity
function test_Permit() public {
    tokenA.approve(address(router), 1 ether);
    tokenB.approve(address(router), 1 ether);
    router.addLiquidity(
        address(tokenA), address(tokenB), 1 ether, 1 ether, 1 ether, 1 ether, address(this), block.timestamp
    );
    address pairAddress = factory.getPair(address(tokenA), address(tokenB));
    JalaPair pair = JalaPair(pairAddress);
    uint256 liquidity = pair.balanceOf(address(this));
    liquidity = (liquidity * 3) / 10;
    pair.approve(address(router), liquidity);
    vm.expectRevert();
    router.removeLiquidityWithPermit(
        address(tokenA),
        address(tokenB),
        liquidity,
        0.3 ether - 300,
        0.3 ether - 300,
        address(this),
        block.timestamp,
        true,
        1, // this value is for demonstration only
        bytes32(uint256(1)), // this value is for demonstration only
        bytes32(uint256(1)) // this value is for demonstration only
    );
}
```

## Recommendation
Implement permit function in JalaERC20. Reference: https://github.com/Uniswap/v2-core/blob/master/contracts/UniswapV2ERC20.sol.
