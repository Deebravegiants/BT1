### Title
No Method to Withdraw Assets from King Protocol — (`contracts/king-protocol/TokenSwap.sol`)

### Summary
The `TokenSwap.sol` contract exposes `depositToKingProtocol` and `depositMultipleToKingProtocol` to deposit protocol assets into King Protocol in exchange for KING share tokens, but provides no corresponding withdrawal path to redeem those KING tokens back to the original assets. The only recovery route is a secondary-market swap of KING tokens, which is entirely liquidity-dependent.

### Finding Description
`TokenSwap.sol` implements two deposit-side functions:

- `depositToKingProtocol(address asset, uint256 amount)` — approves and calls `kingProtocol.deposit(tokens, amounts, address(this))`, receiving KING share tokens into the contract.
- `depositMultipleToKingProtocol(address[] assets, uint256[] amounts)` — same flow for multiple assets. [1](#0-0) 

The `IKingProtocol` interface used by `TokenSwap.sol` exposes only two functions:

```solidity
function deposit(address[] memory _tokens, uint256[] memory _amounts, address _receiver) external;
function previewDeposit(address[] memory _tokens, uint256[] memory _amounts) external view returns (uint256 shareToMint, uint256 depositFee);
``` [2](#0-1) 

There is no `withdraw`, `redeem`, or equivalent function in the interface, and no such function exists anywhere in `TokenSwap.sol`. Once assets are deposited into King Protocol, the contract holds KING share tokens with no on-chain path to convert them back to the original assets through the protocol's own code.

### Impact Explanation
Any assets deposited into King Protocol via `TokenSwap.sol` are effectively locked from the protocol's perspective. The KING tokens accumulate in the contract with no redemption mechanism. If the admin/manager needs to recover those assets — for example, to rebalance, to service user withdrawals, or in response to a King Protocol issue — the only available path is a secondary-market swap of KING tokens, which is entirely dependent on external liquidity. Under illiquid conditions this constitutes a **temporary (or permanent) freezing of protocol-controlled funds**.

**Impact: Low–Medium** — contract fails to deliver promised asset recovery; under adverse liquidity conditions, funds are temporarily frozen.

### Likelihood Explanation
`depositToKingProtocol` is a normal operational function callable by `ADMIN_ROLE` or `MANAGER_ROLE`. It is expected to be called in the ordinary course of yield management. Once called, the missing withdrawal path is immediately relevant. The likelihood that the admin/manager will need to withdraw at some point (rebalancing, emergency, protocol wind-down) is high.

**Likelihood: Medium**

### Recommendation
Add a `withdrawFromKingProtocol` (or `redeemFromKingProtocol`) function to `TokenSwap.sol` that calls the King Protocol's redemption interface to convert KING share tokens back to the underlying assets. The `IKingProtocol` interface should be extended to include the corresponding `withdraw`/`redeem` selector. This mirrors the pattern already present for other integrations in the codebase (e.g., Aave integration in `LRTWithdrawalManager.sol` exposes both `_depositToAave` and `_withdrawFromAave`). [3](#0-2) 

### Proof of Concept
1. Admin calls `TokenSwap.depositToKingProtocol(stETH, 1000e18)`.
2. `TokenSwap.sol` approves King Protocol, calls `kingProtocol.deposit([stETH], [1000e18], address(this))`, and receives KING share tokens.
3. Admin later needs to recover the stETH (e.g., to fund user withdrawals or rebalance).
4. No `withdrawFromKingProtocol` function exists in `TokenSwap.sol`.
5. No withdrawal selector exists in `IKingProtocol`.
6. The only recovery path is selling KING tokens on a secondary market — which may be illiquid or unavailable — leaving the stETH effectively frozen inside King Protocol from the protocol's perspective. [1](#0-0) [4](#0-3)

### Citations

**File:** contracts/king-protocol/TokenSwap.sol (L151-190)
```text
        whenNotPaused
        onlyAdminOrManager
        returns (uint256 shareReceived)
    {
        if (amount == 0) {
            revert ZeroAmount();
        }

        if (!supportedTokens[asset]) {
            revert UnsupportedAsset();
        }

        IERC20 assetToken = IERC20(asset);
        uint256 contractBalance = assetToken.balanceOf(address(this));

        if (contractBalance < amount) {
            revert InsufficientBalance();
        }

        // Create arrays for the deposit call
        address[] memory tokens = new address[](1);
        uint256[] memory amounts = new uint256[](1);
        tokens[0] = asset;
        amounts[0] = amount;

        // Preview the deposit to get expected shares
        (uint256 expectedShares,) = kingProtocol.previewDeposit(tokens, amounts);
        shareReceived = expectedShares;

        // Approve King Protocol to spend the tokens
        assetToken.forceApprove(address(kingProtocol), amount);

        // Deposit to King Protocol
        kingProtocol.deposit(tokens, amounts, address(this));

        // Reset approval after successful deposit
        assetToken.forceApprove(address(kingProtocol), 0);

        emit TokensDeposited(asset, amount, shareReceived, msg.sender);
    }
```

**File:** contracts/king-protocol/IKingProtocol.sol (L1-25)
```text
// SPDX-License-Identifier: BUSL-1.1
pragma solidity 0.8.27;

/// @title IKingProtocol - Interface for King Protocol
/// @notice Interface for depositing assets into King Protocol and receiving KING tokens
interface IKingProtocol {
    /// @notice Deposit multiple assets into King Protocol
    /// @param _tokens Array of token addresses to deposit
    /// @param _amounts Array of amounts to deposit
    /// @param _receiver Recipient of the minted share tokens
    function deposit(address[] memory _tokens, uint256[] memory _amounts, address _receiver) external;

    /// @notice Preview the expected share tokens and fees for a deposit
    /// @param _tokens Array of token addresses to deposit
    /// @param _amounts Array of amounts to deposit
    /// @return shareToMint Amount of share tokens to mint (after fees)
    /// @return depositFee Amount of deposit fee
    function previewDeposit(
        address[] memory _tokens,
        uint256[] memory _amounts
    )
        external
        view
        returns (uint256 shareToMint, uint256 depositFee);
}
```

**File:** contracts/LRTWithdrawalManager.sol (L894-921)
```text
    function _depositToAave(uint256 amount) internal {
        if (amount == 0) return;

        aaveWETHGateway.depositETH{ value: amount }(aavePool, address(this), 0);
        totalETHDepositedToAave += amount;

        emit ETHDepositedToAave(amount, totalETHDepositedToAave);
    }

    /// @dev Withdraw ETH from Aave v3
    /// @param amount The amount of ETH to withdraw
    function _withdrawFromAave(uint256 amount) internal returns (uint256 withdrawnAmount) {
        if (amount == 0) return 0;

        uint256 aaveBalance = aaveAWETH.balanceOf(address(this));
        if (aaveBalance == 0) revert InsufficientAaveBalance();

        // Only withdraw up to the principal amount (don't use accrued interest for user withdrawals)
        uint256 withdrawablePrincipal = aaveBalance < totalETHDepositedToAave ? aaveBalance : totalETHDepositedToAave;

        withdrawnAmount = amount > withdrawablePrincipal ? withdrawablePrincipal : amount;
        if (withdrawnAmount == 0) return 0;

        aaveWETHGateway.withdrawETH(aavePool, withdrawnAmount, address(this));
        totalETHDepositedToAave -= withdrawnAmount;

        emit ETHWithdrawnFromAave(withdrawnAmount, totalETHDepositedToAave);
    }
```
