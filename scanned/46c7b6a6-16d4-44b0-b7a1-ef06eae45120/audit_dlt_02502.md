# [?] OnyxProtocol - Precission Loss Vulnerability

## Summary
Severity: Unknown
Chain: Ethereum
Component: OnyxProtocol
Published: 2023-11-01
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-11/OnyxProtocol_exp.sol
Type: defi-exploit-poc

## Details
Lost: ~$2M
References:
- https://twitter.com/Phalcon_xyz/status/1719697319824851051
- https://defimon.xyz/attack/mainnet/0xf7c21600452939a81b599017ee24ee0dfd92aaaccd0a55d02819a7658a6ef635
- https://twitter.com/DecurityHQ/status/1719657969925677161

```solidity
contract ContractTest is Test {
    IAaveFlashloan private constant AaveV3 = IAaveFlashloan(0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2);
    IWETH private constant WETH = IWETH(payable(0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2));
    IERC20 private constant PEPE = IERC20(0x6982508145454Ce325dDbE47a25d4ec3d2311933);
    IUSDC private constant USDC = IUSDC(0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48);
    IUSDT private constant USDT = IUSDT(0xdAC17F958D2ee523a2206206994597C13D831ec7);
    IERC20 private constant PAXG = IERC20(0x45804880De22913dAFE09f4980848ECE6EcbAf78);
    IERC20 private constant DAI = IERC20(0x6B175474E89094C44Da98b954EedeAC495271d0F);
    IERC20 private constant WBTC = IERC20(0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599);
    IERC20 private constant LINK = IERC20(0x514910771AF9Ca656af840dff83E8264EcF986CA);
    ICErc20Delegate private constant oPEPE = ICErc20Delegate(payable(0x5FdBcD61bC9bd4B6D3FD1F49a5D253165Ea11750));
    ICErc20Delegate private constant oUSDC = ICErc20Delegate(payable(0x8f35113cFAba700Ed7a907D92B114B44421e412A));
    ICErc20Delegate private constant oUSDT = ICErc20Delegate(payable(0xbCed4e924f28f43a24ceEDec69eE21ed4D04D2DD));
    ICErc20Delegate private constant oPAXG = ICErc20Delegate(payable(0x0C19D213e9f2A5cbAA4eC6E8eAC55a22276b0641));
    ICErc20Delegate private constant oDAI = ICErc20Delegate(payable(0x830DAcD5D0a62afa92c9Bc6878461e9cD317B085));
    ICErc20Delegate private constant oBTC = ICErc20Delegate(payable(0x1933f1183C421d44d531Ed40A5D2445F6a91646d));
    ICErc20Delegate private constant oLINK = ICErc20Delegate(payable(0xFEe4428b7f403499C50a6DA947916b71D33142dC));
    crETH private constant oETHER = crETH(payable(0x714bD93aB6ab2F0bcfD2aEaf46A46719991d0d79));
    Uni_Pair_V2 private constant PEPE_WETH = Uni_Pair_V2(0xA43fe16908251ee70EF74718545e4FE6C5cCEc9f);
    Uni_Pair_V2 private constant USDC_WETH = Uni_Pair_V2(0xB4e16d0168e52d35CaCD2c6185b44281Ec28C9Dc);
    Uni_Pair_V2 private constant WETH_USDT = Uni_Pair_V2(0x0d4a11d5EEaaC28EC3F61d100daF4d40471f1852);
    Uni_Pair_V2 private constant PAXG_WETH = Uni_Pair_V2(0x9C4Fe5FFD9A9fC5678cFBd93Aa2D4FD684b67C4C);
    Uni_Pair_V2 private constant DAI_WETH = Uni_Pair_V2(0xA478c2975Ab1Ea89e8196811F51A7B7Ade33eB11);
    Uni_Pair_V2 private constant WBTC_WETH = Uni_Pair_V2(0xBb2b8038a1640196FbE3e38816F3e67Cba72D940);
    Uni_Pair_V2 private constant LINK_WETH = Uni_Pair_V2(0xa2107FA5B38d9bbd2C461D6EDf11B11A50F6b974);
    Uni_Router_V2 private constant Router = Uni_Router_V2(0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D);

    function setUp() public {
        vm.createSelectFork("mainnet", 18_476_512);
        vm.label(address(AaveV3), "AaveV3");
        vm.label(address(WETH), "WETH");
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-11/OnyxProtocol_exp.sol_
