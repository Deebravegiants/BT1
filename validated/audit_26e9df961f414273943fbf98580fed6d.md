Audit Report

## Title
Cross-Token Withdrawal Allows Draining of Specific Token Reserves - (File: `contracts/L2/RsETHTokenWrapper.sol`)

## Summary
`RsETHTokenWrapper` issues a single fungible `wrsETH` token for deposits of any allowed token, but maintains no per-token reserve accounting. A holder of `wrsETH` minted from `tokenA` can call `withdraw(tokenB, amount)` to redeem against `tokenB` reserves, leaving `tokenB` depositors unable to withdraw their original asset. Total value in the system is not destroyed, but the contract fails to deliver the specific token a depositor is owed.

## Finding Description
`_deposit` mints `wrsETH` 1:1 for any allowed token without recording which token was deposited by which user: [1](#0-0) 

`_withdraw` only checks `allowedTokens[_asset]`, then burns `wrsETH` and transfers the requested asset — with no check that the caller ever deposited that specific token: [2](#0-1) 

The `allowedTokens` mapping tracks only whether a token is permitted, not per-user or per-token reserve balances: [3](#0-2) 

There is no other accounting structure anywhere in the contract that would prevent cross-token redemption. [4](#0-3) 

## Impact Explanation
**Low. Contract fails to deliver promised returns, but doesn't lose value.**

Concrete scenario: userA deposits `tokenA`, userB deposits `tokenB`. userA calls `withdraw(tokenB, amount)`, draining the `tokenB` reserve. userB's subsequent `withdraw(tokenB, amount)` reverts. userB may still withdraw `tokenA` instead, so aggregate value is preserved — but the contract fails to return the specific asset each depositor is owed. This matches the allowed Low impact class exactly.

## Likelihood Explanation
The precondition is that a second token has been added via `addAllowedToken` (requires `TIMELOCK_ROLE`). This is a normal, expected protocol operation — the `reinitialize` function already demonstrates the design intent to support multiple tokens: [5](#0-4) [6](#0-5) 

Once a second token exists, any unprivileged user can trigger the exploit with a single `withdraw` call. No special permissions, flash loans, or victim mistakes are required.

## Recommendation
Track per-token reserves explicitly. Maintain a `mapping(address token => uint256 reserve)` that increments in `_deposit` and decrements in `_withdraw`, reverting if the per-token reserve is insufficient. Alternatively, issue separate wrapper tokens per underlying asset rather than a single fungible `wrsETH`.

## Proof of Concept
```solidity
function testCrossTokenWithdrawal() public {
    // Precondition: two allowed tokens exist (tokenA added at init, tokenB via addAllowedToken)
    // userA deposits tokenA
    tokenA.approve(address(wrapper), 100e18);
    wrapper.deposit(address(tokenA), 100e18);

    // userB deposits tokenB
    vm.startPrank(userB);
    tokenB.approve(address(wrapper), 100e18);
    wrapper.deposit(address(tokenB), 100e18);
    vm.stopPrank();

    // userA withdraws tokenB (different from what they deposited)
    wrapper.withdraw(address(tokenB), 100e18);
    assertEq(tokenB.balanceOf(address(this)), 100e18); // userA received tokenB

    // userB can no longer redeem wrsETH for tokenB — reserve is empty
    vm.prank(userB);
    vm.expectRevert(); // ERC20: transfer amount exceeds balance
    wrapper.withdraw(address(tokenB), 100e18);
}
```

### Citations

**File:** contracts/L2/RsETHTokenWrapper.sol (L20-30)
```text
contract RsETHTokenWrapper is Initializable, AccessControlUpgradeable, ERC20Upgradeable, ERC20PermitUpgradeable {
    using SafeERC20Upgradeable for ERC20Upgradeable;

    /// @dev The address of the alternative RsETH token
    mapping(address allowedToken => bool isAllowed) public allowedTokens;

    bytes32 public constant MINTER_ROLE = keccak256("MINTER_ROLE");
    bytes32 public constant BRIDGER_ROLE = keccak256("BRIDGER_ROLE");
    bytes32 public constant TIMELOCK_ROLE = keccak256("TIMELOCK_ROLE");

    error TokenNotAllowed();
```

**File:** contracts/L2/RsETHTokenWrapper.sol (L47-49)
```text
    function reinitialize(address _altRsETH) external reinitializer(2) onlyRole(DEFAULT_ADMIN_ROLE) {
        _addAllowedToken(_altRsETH);
    }
```

**File:** contracts/L2/RsETHTokenWrapper.sol (L120-128)
```text
    function _withdraw(address _asset, address _to, uint256 _amount) internal {
        if (!allowedTokens[_asset]) revert TokenNotAllowed();

        _burn(msg.sender, _amount);

        ERC20Upgradeable(_asset).safeTransfer(_to, _amount);

        emit Withdraw(_asset, msg.sender, _to, _amount);
    }
```

**File:** contracts/L2/RsETHTokenWrapper.sol (L134-141)
```text
    function _deposit(address _asset, address _to, uint256 _amount) internal {
        if (!allowedTokens[_asset]) revert TokenNotAllowed();

        ERC20Upgradeable(_asset).safeTransferFrom(msg.sender, address(this), _amount);

        _mint(_to, _amount);
        emit Deposit(_asset, msg.sender, _to, _amount);
    }
```

**File:** contracts/L2/RsETHTokenWrapper.sol (L174-176)
```text
    function addAllowedToken(address _asset) external onlyRole(TIMELOCK_ROLE) {
        _addAllowedToken(_asset);
    }
```
