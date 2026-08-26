# [?] - dForce - Read-Only-Reentrancy

## Summary
Severity: Unknown
Chain: Arbitrum
Component: dForce
Published: 2023-02-10
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-02/dForce_exp.sol
Type: defi-exploit-poc

## Details
Lost: ~$3.65M
References:
- https://twitter.com/SlowMist_Team/status/1623956763598000129
- https://twitter.com/BlockSecTeam/status/1623901011680333824
- https://twitter.com/peckshield/status/1623910257033617408
- https://arbiscan.io/tx/0x5db5c2400ab56db697b3cc9aa02a05deab658e1438ce2f8692ca009cc45171dd

```solidity
contract ContractTest is Test {
    IERC20 WETH = IERC20(0x82aF49447D8a07e3bd95BD0d56f35241523fBab1);
    IERC20 USDC = IERC20(0xFF970A61A04b1cA14834A43f5dE4533eBDDB5CC8);
    IERC20 USX = IERC20(0x641441c631e2F909700d2f41FD87F0aA6A6b4EDb);
    IERC20 WSTETH = IERC20(0x5979D7b546E38E414F7E9822514be443A4800529);
    IERC20 WSTETHCRV = IERC20(0xDbcD16e622c95AcB2650b38eC799f76BFC557a0b);
    IERC20 WSTETHCRVGAUGE = IERC20(0x098EF55011B6B8c99845128114A9D9159777d697);
    IVWSTETHCRVGAUGE VWSTETHCRVGAUGE = IVWSTETHCRVGAUGE(0x2cE498b79C499c6BB64934042eBA487bD31F75ea);
    IBalancerVault balancer = IBalancerVault(0xBA12222222228d8Ba445958a75a0704d566BF2C8);
    IAaveFlashloan aaveV3 = IAaveFlashloan(0x794a61358D6845594F94dc1DB02A252b5b4814aD);
    IAaveFlashloan Radiant = IAaveFlashloan(0x2032b9A8e9F7e76768CA9271003d3e43E1616B1F);
    uniswapV3Flash UniV3Flash = uniswapV3Flash(0xC31E54c7a869B9FcBEcc14363CF510d1c41fa443);
    Uni_Pair_V2 SLP1 = Uni_Pair_V2(0xB7E50106A5bd3Cf21AF210A755F9C8740890A8c9);
    Uni_Pair_V2 SLP2 = Uni_Pair_V2(0x905dfCD5649217c42684f23958568e533C711Aa3);
    Uni_Pair_V2 SLP3 = Uni_Pair_V2(0x0C1Cf6883efA1B496B01f654E247B9b419873054);
    Uni_Pair_V2 ZLP = Uni_Pair_V2(0x8b8149Dd385955DC1cE77a4bE7700CCD6a212e65);
    ISwapFlashLoan swapFlashLoan = ISwapFlashLoan(0xa067668661C84476aFcDc6fA5D758C4c01C34352);
    ICurvePools curvePool = ICurvePools(0x6eB2dc694eB516B16Dc9FBc678C60052BbdD7d80);
    ICointroller cointroller = ICointroller(0x61afB763bc265bD372e8Af8daC00196C9A5eCea0);
    address aArbWETH = 0xe50fA9b3c56FfB159cB0FCA61F5c9D750e8128c8;
    address rWETH = 0x15b53d277Af860f51c3E6843F8075007026BBb3a;
    IDForce dForceContract = IDForce(0xC462fF1063172BAC6f6823A17ED181a0586f0FC8);
    IPriceOracleV2 PriceOracle = IPriceOracleV2(0x15962427A9795005c640A6BF7f99c2BA1531aD6d);
    IcurveYSwap curveYSwap = IcurveYSwap(0x2ce5Fd6f6F4a159987eac99FF5158B7B62189Acf);
    GMXVAULT GMXVault = GMXVAULT(0x489ee077994B6658eAfA855C308275EAd8097C4A);
    Borrower borrower;
    address victimAddress2 = 0x916792f7734089470de27297903BED8a4630b26D;
    uint256 balancerFlashloanAmount;
    uint256 aaveV3FlashloanAmount;
    uint256 UniV3FlashloanAmount;
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-02/dForce_exp.sol_
