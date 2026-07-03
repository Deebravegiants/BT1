### Title
BRIDGER_ROLE can steal accumulated protocol fees via `withdrawFees` - (File: contracts/pools/RSETHPoolV2ExternalBridge.sol, contracts/pools/RSETHPoolV3WithNativeChainBridge.sol)

---

### Summary
The `withdrawFees` functions in `RSETHPoolV2ExternalBridge` and `RSETHPoolV3WithNativeChainBridge` are gated only by `BRIDGER_ROLE`, a lower-privileged operational role whose intended purpose is to bridge assets between L2 and L1. These functions accept a caller-supplied `receiver` address and transfer all accumulated protocol fee balances to it. A BRIDGER_ROLE holder can therefore direct all protocol fees to themselves or any address they control, stealing yield that belongs to the protocol treasury.

---

### Finding Description
In `RSETHPoolV2ExternalBridge.sol`, the fee-withdrawal function is:

```solidity
function withdrawFees(address receiver) external nonReentrant onlyRole(BRIDGER_ROLE) {
    uint256 amountToSendInETH = feeEarnedInETH;
    feeEarnedInETH = 0;
    (bool success,) = payable(receiver).call{ value: amountToSendInETH }("");
    if (!success) revert TransferFailed();
    emit FeesWithdrawn(amountToSendInETH);
}
``` [1](#0-0) 

In `RSETHPoolV3WithNativeChainBridge.sol`, two overloads exist — one for ETH fees and one for ERC-20 token fees — both gated only by `BRIDGER_ROLE`:

```solidity
function withdrawFees(address receiver) external nonReentrant onlyRole(BRIDGER_ROLE) { ... }
function withdrawFees(address receiver, address token) external nonReentrant onlySupportedToken(token) onlyRole(BRIDGER_ROLE) { ... }
``` [2](#0-1) 

The `receiver` parameter is entirely caller-controlled. There is no check that `receiver` equals a fixed treasury address, the `DEFAULT_ADMIN_ROLE` holder, or any other protocol-controlled address. The BRIDGER_ROLE is defined as a distinct, lower-privileged operational role:

```solidity
bytes32 public constant BRIDGER_ROLE = keccak256("BRIDGER_ROLE");
``` [3](#0-2) 

The role hierarchy in these contracts separates `DEFAULT_ADMIN_ROLE`, `TIMELOCK_ROLE`, `BRIDGER_ROLE`, `OPERATOR_ROLE`, and `PAUSER_ROLE`. Fee withdrawal is a treasury-level operation that should be restricted to `DEFAULT_ADMIN_ROLE` or `TIMELOCK_ROLE`, not to the bridging operator. The Frax analog (`recoverERC20` callable by token managers) is structurally identical: a function that moves protocol-owned tokens is accessible to a role whose intended scope is narrower than treasury management.

---

### Impact Explanation
A BRIDGER_ROLE holder calls `withdrawFees(attackerAddress)` (or the token overload) and receives the entire accumulated `feeEarnedInETH` / `feeEarnedInToken[token]` balance. These balances represent protocol yield collected from every swap performed by users of the pool. The theft is immediate and complete — the state variable is zeroed before the transfer, so no re-entry or race condition is needed. Impact: **High — theft of unclaimed yield**. [2](#0-1) 

---

### Likelihood Explanation
The BRIDGER_ROLE is an operational role granted to an off-chain bridging service or bot. It is a non-admin role that can be granted to external parties. As in the Frax scenario ("Eve tricks Frax Finance into making her a token manager"), a party legitimately granted BRIDGER_ROLE — or one whose key is later reused — can exploit this at any time without any additional preconditions. No oracle manipulation, governance capture, or front-running is required. The call is a single transaction. Likelihood: **Medium** (requires a malicious or socially-engineered BRIDGER_ROLE grantee, but no technical barrier once the role is held).

---

### Recommendation
Restrict `withdrawFees` to `DEFAULT_ADMIN_ROLE` or `TIMELOCK_ROLE`. If the bridging operator genuinely needs to trigger fee disbursement, hard-code the destination to a fixed treasury address stored in contract state (settable only by admin), removing the caller-supplied `receiver` parameter entirely. This mirrors the convention described in the external report: recovery/withdrawal functions should send funds only to a pre-approved, admin-controlled address.

---

### Proof of Concept
1. Protocol admin grants `BRIDGER_ROLE` to address `Eve`.
2. Users swap ETH for wrsETH over time; `feeEarnedInETH` accumulates to, say, 10 ETH.
3. Eve calls `RSETHPoolV2ExternalBridge.withdrawFees(Eve)`.
4. The contract sets `feeEarnedInETH = 0` and transfers 10 ETH to Eve.
5. Protocol treasury receives nothing; all accumulated swap fees are stolen.

The same attack applies to `RSETHPoolV3WithNativeChainBridge` for both ETH fees (`withdrawFees(Eve)`) and ERC-20 token fees (`withdrawFees(Eve, tokenAddress)`). [1](#0-0) [4](#0-3)

### Citations

**File:** contracts/pools/RSETHPoolV2ExternalBridge.sol (L49-50)
```text
    bytes32 public constant BRIDGER_ROLE = keccak256("BRIDGER_ROLE");
    bytes32 public constant TIMELOCK_ROLE = keccak256("TIMELOCK_ROLE");
```

**File:** contracts/pools/RSETHPoolV2ExternalBridge.sol (L448-457)
```text
    /// @dev Withdraws fees earned by the pool
    function withdrawFees(address receiver) external nonReentrant onlyRole(BRIDGER_ROLE) {
        // withdraw fees in ETH
        uint256 amountToSendInETH = feeEarnedInETH;
        feeEarnedInETH = 0;
        (bool success,) = payable(receiver).call{ value: amountToSendInETH }("");
        if (!success) revert TransferFailed();

        emit FeesWithdrawn(amountToSendInETH);
    }
```

**File:** contracts/pools/RSETHPoolV3WithNativeChainBridge.sol (L487-513)
```text
    function withdrawFees(address receiver) external nonReentrant onlyRole(BRIDGER_ROLE) {
        // withdraw fees in ETH
        uint256 amountToSendInETH = feeEarnedInETH;
        feeEarnedInETH = 0;
        (bool success,) = payable(receiver).call{ value: amountToSendInETH }("");
        if (!success) revert TransferFailed();

        emit FeesWithdrawn(amountToSendInETH);
    }

    /// @dev Withdraws fees earned by the pool in a specific token
    function withdrawFees(
        address receiver,
        address token
    )
        external
        nonReentrant
        onlySupportedToken(token)
        onlyRole(BRIDGER_ROLE)
    {
        // withdraw fees in token
        uint256 amountToSendInToken = feeEarnedInToken[token];
        feeEarnedInToken[token] = 0;
        IERC20(token).safeTransfer(receiver, amountToSendInToken);

        emit FeesWithdrawn(amountToSendInToken, token);
    }
```
