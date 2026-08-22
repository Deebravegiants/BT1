# [?] - Lodestar - FlashLoan price manipulation

## Summary
Severity: Unknown
Chain: Arbitrum
Component: Lodestar
Published: 2022-12-11
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2022-12/Lodestar_exp.sol
Type: defi-exploit-poc

## Details
Lost: $4M
References:
- https://twitter.com/SolidityFinance/status/1601684150456438784
- https://blog.lodestarfinance.io/post-mortem-summary-13f5fe0bb336
- https://arbiscan.io/tx/0xc523c6307b025ebd9aef155ba792d1ba18d5d83f97c7a846f267d3d9a3004e8c

```solidity
contract ContractTest is Test {
    IERC20 USDC = IERC20(0xFF970A61A04b1cA14834A43f5dE4533eBDDB5CC8);
    IERC20 DAI = IERC20(0xDA10009cBd5D07dd0CeCc66161FC93D7c9000da1);
    IERC20 WETH = IERC20(0x82aF49447D8a07e3bd95BD0d56f35241523fBab1);
    IERC20 USDT = IERC20(0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9);
    IERC20 FRAX = IERC20(0x17FC002b466eEc40DaE837Fc4bE5c67993ddBd6F);
    IERC20 sGLP = IERC20(0x2F546AD4eDD93B956C8999Be404cdCAFde3E89AE);
    IERC20 MIM = IERC20(0xFEa7a6a0B346362BF88A9e4A88416B77a57D6c2A);
    IERC20 WBTC = IERC20(0x2f2a2543B76A4166549F7aaB2e75Bef0aefC5B0f);
    IERC20 PlvGlpToken = IERC20(0x5326E71Ff593Ecc2CF7AcaE5Fe57582D6e74CFF1);
    IAaveFlashloan AaveFlash = IAaveFlashloan(0x794a61358D6845594F94dc1DB02A252b5b4814aD);
    IAaveFlashloan Radiant = IAaveFlashloan(0x2032b9A8e9F7e76768CA9271003d3e43E1616B1F);
    uniswapV3Flash UniV3Flash1 = uniswapV3Flash(0xC31E54c7a869B9FcBEcc14363CF510d1c41fa443);
    uniswapV3Flash UniV3Flash2 = uniswapV3Flash(0x50450351517117Cb58189edBa6bbaD6284D45902);
    uniswapV3Flash UniV3Flash3 = uniswapV3Flash(0x13398E27a21Be1218b6900cbEDF677571df42A48);
    Uni_Pair_V2 Pair = Uni_Pair_V2(0x905dfCD5649217c42684f23958568e533C711Aa3);
    GMXRouter Router = GMXRouter(0xaBBc5F99639c9B6bCb58544ddf04EFA6802F4064);
    GMXReward Reward = GMXReward(0xA906F338CB21815cBc4Bc87ace9e68c87eF8d8F1);
    IUnitroller unitroller = IUnitroller(0x8f2354F9464514eFDAe441314b8325E97Bf96cdc);
    ICErc20Delegate IUSDC = ICErc20Delegate(0x5E3F2AbaECB51A182f05b4b7c0f7a5da1942De90);
    ICErc20Delegate lplvGLP = ICErc20Delegate(0xCC25daC54A1a62061b596fD3Baf7D454f34c56fF);
    ICErc20Delegate IETH = ICErc20Delegate(0xb4d58C1F5870eFA4B05519A72851227F05743273);
    ICErc20Delegate IMIM = ICErc20Delegate(0x46178d84339A04f140934EE830cDAFDAcD29Fba9);
    ICErc20Delegate IUSDT = ICErc20Delegate(0xeB156f76Ef69be485c18C297DeE5c45390345187);
    ICErc20Delegate IFRAX = ICErc20Delegate(0x5FfA22244D8273d899B6C20CEC12A88a7Cd9E460);
    ICErc20Delegate IDAI = ICErc20Delegate(0x7a668F56AffD511FFc83C31666850eAe9FD5BCC8);
    ICErc20Delegate IWBTC = ICErc20Delegate(0xD2835B08795adfEfa0c2009B294ae84B08C6a67e);
    SwapFlashLoan swapFlashLoan = SwapFlashLoan(0x401AFbc31ad2A3Bc0eD8960d63eFcDEA749b4849);
    GlpDepositor depositor = GlpDepositor(0x13F0D29b5B83654A200E4540066713d50547606E);
    address GlpManager = 0x321F653eED006AD1C29D174e17d96351BDe22649;

```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2022-12/Lodestar_exp.sol_
