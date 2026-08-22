# [?] yearnFinance - Misconfiguration

## Summary
Severity: Unknown
Chain: Ethereum
Component: YearnFinance
Published: 2023-04-13
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-04/YearnFinance_exp.sol
Type: defi-exploit-poc

## Details
Lost: $11.6M
References:
- https://twitter.com/cmichelio/status/1646422861219807233
- https://twitter.com/BeosinAlert/status/1646481687445114881
- https://etherscan.io/tx/0x055cec4fa4614836e54ea2e5cd3d14247ff3d61b85aa2a41f8cc876d131e0328
- https://etherscan.io/tx/0xd55e43c1602b28d4fd4667ee445d570c8f298f5401cf04e62ec329759ecda95d

```solidity
contract ContractTest is Test {
    uint256 internal constant FLASHLOAN_DAI_AMOUNT = 5_000_000 * 1e18;
    uint256 internal constant FLASHLOAN_USDC_AMOUNT = 5_000_000 * 1e6;
    uint256 internal constant FLASHLOAN_USDT_AMOUNT = 2_000_000 * 1e6;
    uint256 internal constant YUSDT_DEPOSIT_USDT_AMOUNT = 900_000 * 1e6;

    address[] public aaveV1UsdtDebtUsers = [
        0xCCaAa3feCdd625CB4e0EdC2728121011caede655,
        0xfda180bbadb213Ce91C7D70771031B48bCaA09a7,
        0x929CB4b2501350dA5a33FDA2F6Fd9C818da65116,
        0x5fa23A19B37ae7c7CD49db44f459142A586Cc392,
        0x584495a3F4033f913aaDd0789fe5787aB0852Eac,
        0xe7a6B9d6EC7CDEA7487D6D1d83e0fB254d7b9653,
        0x63fB86F437AEe0dad657040563Dbb6bA7CA23d70,
        0xEFCFbCc6693B137fc2Fb62149a2cc48E1946e585,
        0x66541D275dA05a8513948a9D0f9547C6FCc62eF5,
        0x51A23045dB018780dd40C890C62368C187E8d179,
        0xe84A061897afc2e7fF5FB7e3686717C528617487,
        0xC96c7536D20808a39FBcE9949B3511E4198290C5,
        0xf398F0d68A70E5a1C78b03e7CF0F6BE54dA2d782,
        0x165f1a77C9861b8B943A9B60E9e7503076fD8d84,
        0x86683cB61BB9EBB8893Db3b82271166879c2502d,
        0x286a4289Bb294A961BD8a13A9922428b12549f6A,
        0xa0357704F7B78306f401A03d08d1D7b8a6555AcF,
        0x67659F1105a093023CdA611B9e3e09151700942d,
        0xB603318b7Ce72caAf8d54e697349398401CCc5f7,
        0xb6BF3d48e0808EeF3a5fBc92bB470aa17b67Ee9E,
        0xb50A98b218968d9D6ec895BE6850aB2807B763dc,
        0xeB874df4951bA627CFbe85b0CdB79e2ed7Bd30F7,
        0xFFbC745D5d91C8FC3E2bC6D65256EA596410811C,
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-04/YearnFinance_exp.sol_
