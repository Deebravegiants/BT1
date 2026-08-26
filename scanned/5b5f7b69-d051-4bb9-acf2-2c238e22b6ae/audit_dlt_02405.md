# [?] Conic Finance - Read-Only-Reentrancy && MisConfiguration

## Summary
Severity: Unknown
Chain: Ethereum
Component: Conic
Published: 2023-07-21
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-07/Conic_exp.sol
Type: defi-exploit-poc

## Details
Lost: ~$3.25M

```solidity
contract ContractTest is Test {
    IWFTM WETH = IWFTM(payable(0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2));
    IERC20 rETH = IERC20(0xae78736Cd615f374D3085123A210448E74Fc6393);
    IERC20 stETH = IERC20(0xae7ab96520DE3A18E5e111B5EaAb095312D7fE84);
    IERC20 cbETH = IERC20(0xBe9895146f7AF43049ca1c1AE358B0541Ea49704);
    IERC20 steCRV = IERC20(0x06325440D014e39736583c165C2963BA99fAf14E);
    IERC20 cbETH_ETH_LP = IERC20(0x5b6C539b224014A09B3388e51CaAA8e354c959C8);
    IERC20 rETH_ETH_LP = IERC20(0x6c38cE8984a890F5e46e6dF6117C26b3F1EcfC9C);
    IERC20 cncETH = IERC20(0x3565A68666FD3A6361F06f84637E805b727b4A47);
    ICurve rETH_ETH_Pool = ICurve(0x0f3159811670c117c372428D4E69AC32325e4D0F);
    ICurve cbETH_ETH_Pool = ICurve(0x5FAE7E604FC3e24fd43A72867ceBaC94c65b404A);
    IBalancerVault Balancer = IBalancerVault(0xBA12222222228d8Ba445958a75a0704d566BF2C8);
    IAaveFlashloan aaveV2 = IAaveFlashloan(0x7d2768dE32b0b80b7a3454c06BdAc94A69DDc7A9);
    IAaveFlashloan aaveV3 = IAaveFlashloan(0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2);
    ICurvePool LidoCurvePool = ICurvePool(0xDC24316b9AE028F1497c275EB9192a3Ea0f67022);
    IConicEthPool ConicEthPool = IConicEthPool(0xBb787d6243a8D450659E09ea6fD82F1C859691e9);
    IGenericOracleV2 Oracle = IGenericOracleV2(0x286eF89cD2DA6728FD2cb3e1d1c5766Bcea344b0);
    uint256 nonce;

    function setUp() public {
        vm.createSelectFork("mainnet", 17_740_954);
        vm.label(address(WETH), "WETH");
        vm.label(address(steCRV), "steCRV");
        vm.label(address(cbETH_ETH_LP), "cbETH_ETH_LP");
        vm.label(address(rETH_ETH_LP), "rETH_ETH_LP");
        vm.label(address(cncETH), "cncETH");
        vm.label(address(stETH), "stETH");
        vm.label(address(rETH), "rETH");
        vm.label(address(cbETH), "cbETH");
        vm.label(address(LidoCurvePool), "LidoCurvePool");
        vm.label(address(rETH_ETH_Pool), "rETH_ETH_Pool");
        vm.label(address(cbETH_ETH_Pool), "cbETH_ETH_Pool");
        vm.label(address(cncETH), "cncETH");
        vm.label(address(Balancer), "Balancer");
        vm.label(address(aaveV3), "aaveV3");
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-07/Conic_exp.sol_
