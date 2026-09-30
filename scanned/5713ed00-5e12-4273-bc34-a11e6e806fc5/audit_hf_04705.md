# [M] Mint and sales can be dossed due to lack of approval to zero

## Summary
Severity: Medium
Contest weight: 0.5951
Dataset id: 22492
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The lack of approval to 0 to the dvp contract, and the fee managers during DVP mints and sales will cause that subsequent transactions involving approval of these contracts to spend the basetoken will fail, breaking their functionality.

When DVPs are to be minted and sold through the PositionManager, the mint and sell functions are invoked. The first issue appears here, where the DVP contract is approved to spend the basetoken using the OpenZeppelin's safeApprove function, without first approving to zero. Further down the line, the mint and sell functions make calls to the DVP contract to mint and burn DVP respectively.

The _mint and _burn functions in the DVP contract approves the fee manager to spend the fee - vaultFee/netFee. This issue here is that OpenZeppelin's safeApprove() function does not allow changing a non-zero allowance to another non-zero allowance. This will therefore cause all subsequent approval of the basetoken to fail after the first approval, dossing the contract's minting and selling/burning functionality.

OpenZeppelin's safeApprove() will revert if the account already is approved and the new safeApprove() is done with a non-zero value.
```solidity
function safeApprove(
    IERC20 token,
    address spender,
    uint256 value
) internal {
    // safeApprove should only be called when setting an initial allowance,
    // or when resetting it to zero. To increase and decrease it, use
    // 'safeIncreaseAllowance' and 'safeDecreaseAllowance'
    require(
        (value == 0) || (token.allowance(address(this), spender) == 0),
        "SafeERC20: approve from non-zero to non-zero allowance"
    );
    _callOptionalReturn(token, abi.encodeWithSelector(token.approve.selector, spender, value));
}
```
This causes that after the first approval for the baseToken has been given, subsequent approvals will fail causing the functions to fail.

a41dd2e51997f64ef3ec017bd/smilee-v2-contracts/src/DVP.sol#L173 The _mint and _burn functions both send a call to approve the feeManager to "pull" the tokens upon the receiveFee function being called. And as can be seen from the snippets, a zero approval is not given first.
```solidity
function _mint(
    address recipient,
    uint256 strike,
    Amount memory amount,
    uint256 expectedPremium,
    uint256 maxSlippage
) internal returns (uint256 premium_) {
    ...
    // Get fees from sender:
    IERC20Metadata(baseToken).safeTransferFrom(msg.sender, address(this), fee - vaultFee);
    IERC20Metadata(baseToken).safeApprove(address(feeManager), fee - vaultFee);
    feeManager.receiveFee(fee - vaultFee);
    ...
}
```
a41dd2e51997f64ef3ec017bd/smilee-v2-contracts/src/DVP.sol#L327
```solidity
function _burn(
    uint256 expiry,
    address recipient,
    uint256 strike,
    Amount memory amount,
    uint256 expectedMarketValue,
    uint256 maxSlippage
) internal returns (uint256 paidPayoff) {
    ....
    feeManager.receiveFee(netFee);
    feeManager.trackVaultFee(address(vault), vaultFee);
    emit Burn(msg.sender);
}
```
a41dd2e51997f64ef3ec017bd/smilee-v2-contracts/src/periphery/PositionManager.sol#L124
```solidity
function mint(
    IPositionManager.MintParams calldata params
) external override returns (uint256 tokenId, uint256 premium) {
    ...
    // Transfer premium:
    IERC20 baseToken = IERC20(dvp.baseToken());
    baseToken.safeTransferFrom(msg.sender, address(this), obtainedPremium);
    // Premium already include fee
    ...
}
```

## Recommendation
1. Approve first to 0;  
2. Update the OpenZeppelin version to the latest and use the forceApprove functions instead;  
3. Refactor the functions to allow for direct transfer of base tokens to the DVP and FeeManager contracts directly.
