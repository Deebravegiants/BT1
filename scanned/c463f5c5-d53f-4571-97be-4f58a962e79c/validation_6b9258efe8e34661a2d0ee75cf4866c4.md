### Title
Missing Contract Existence Check in `LRTConfig._setContract` Allows Setting Critical Protocol Addresses to Non-Contract Addresses - (File: contracts/LRTConfig.sol)

---

### Summary
`LRTConfig._setContract` only validates that the supplied address is non-zero. It performs no `extcodesize` check to confirm that a contract is actually deployed at the address. If a new protocol contract (e.g., `LRT_DEPOSIT_POOL`, `LRT_ORACLE`, `LRT_WITHDRAW_MANAGER`) is registered via a pre-computed CREATE2 address whose deployment subsequently fails silently, the registry will point to an empty address. All downstream callers that resolve the address through `lrtConfig.getContract(...)` and then make external calls will silently succeed (EVM calls to empty addresses return success with empty data), producing undefined behavior across the protocol.

---

### Finding Description
`LRTConfig.setContract` delegates to the private `_setContract`:

```solidity
function _setContract(bytes32 key, address val) private {
    UtilLib.checkNonZeroAddress(val);   // only zero-address guard
    if (contractMap[key] == val) {
        revert ValueAlreadyInUse();
    }
    contractMap[key] = val;
    emit SetContract(key, val);
}
```

`UtilLib.checkNonZeroAddress` is a pure function that only reverts on `address(0)`:

```solidity
function checkNonZeroAddress(address address_) internal pure {
    if (address_ == address(0)) revert ZeroAddressNotAllowed();
}
```

There is no `extcodesize` / `address.code.length` check. Any non-zero address — including one with no deployed bytecode — is accepted and stored in `contractMap`.

The stored addresses are later consumed by critical protocol paths. For example, `LRTOracle._updateRsETHPrice` resolves both `LRT_DEPOSIT_POOL` and `LRT_WITHDRAW_MANAGER` from the registry and calls `.paused()` on them:

```solidity
IPausable lrtDepositPool    = IPausable(lrtConfig.getContract(LRTConstants.LRT_DEPOSIT_POOL));
IPausable withdrawalManager = IPausable(lrtConfig.getContract(LRTConstants.LRT_WITHDRAW_MANAGER));
bool protocolPaused = lrtDepositPool.paused() || withdrawalManager.paused() || paused;
```

A call to `.paused()` on an empty address returns success with zero bytes, which ABI-decodes to `false`. The oracle therefore believes the protocol is active and proceeds to compute and mint protocol fees even when the real contracts are paused or non-existent.

Similarly, `LRTConfig.pauseAll` resolves the same keys and calls `.pause()` on the returned addresses. If any key maps to an empty address, the pause call silently succeeds without actually pausing the real contract, defeating the emergency-stop mechanism.

---

### Impact Explanation
**Medium — Temporary freezing of funds / pause bypass.**

If `LRT_DEPOSIT_POOL` or `LRT_WITHDRAW_MANAGER` is registered to an address with no code:

1. **Pause bypass:** `pauseAll()` silently "pauses" an empty address. The real deposit pool and withdrawal manager remain unpaused, so users can continue to interact with them during an emergency where the admin believes the protocol is halted.
2. **Oracle mis-accounting:** `_updateRsETHPrice` treats the protocol as active (not paused) and mints protocol fees against a stale or incorrect TVL, corrupting the rsETH/ETH exchange rate used for all subsequent deposits and withdrawals.
3. **Broken downstream lookups:** Any contract that calls `lrtConfig.getContract(...)` and then performs a state-changing call on the result will silently succeed with no effect, causing fund flows to be lost or misdirected.

---

### Likelihood Explanation
Low-to-medium. The protocol uses or plans to use CREATE2-based deployments (evidenced by `contracts/utils/CREATE3.sol` and `CREATE3Factory.sol`). A CREATE2 address is computable before deployment. If the admin pre-registers the address in `LRTConfig` before confirming the deployment succeeded — or if the deployment transaction fails and goes unnoticed — the registry will silently point to empty bytecode. No malicious actor is required; a routine upgrade operation is sufficient to trigger the condition.

---

### Recommendation
Add a contract existence check inside `_setContract` before writing to `contractMap`:

```solidity
function _setContract(bytes32 key, address val) private {
    UtilLib.checkNonZeroAddress(val);
    if (val.code.length == 0) revert AddressIsNotContract();
    if (contractMap[key] == val) revert ValueAlreadyInUse();
    contractMap[key] = val;
    emit SetContract(key, val);
}
```

Apply the same guard to `_setToken`, `setRSETH`, and any other setter that stores an address expected to be a contract. Add a code-review checklist item requiring `extcodesize > 0` validation for all contract-address setters.

---

### Proof of Concept

1. Admin pre-computes the CREATE2 address of a new `LRTDepositPool` implementation and calls:
   ```solidity
   lrtConfig.setContract(LRTConstants.LRT_DEPOSIT_POOL, precomputedAddress);
   ```
   The deployment transaction for `precomputedAddress` fails (out-of-gas, constructor revert, etc.) and goes unnoticed. `_setContract` accepts the address because it is non-zero.

2. An emergency arises. The PAUSER calls `lrtConfig.pauseAll()`. Internally:
   ```solidity
   IPausable lrtDepositPool = IPausable(getContract(LRTConstants.LRT_DEPOSIT_POOL));
   // lrtDepositPool == precomputedAddress (no code)
   if (!lrtDepositPool.paused()) lrtDepositPool.pause();
   // Both calls succeed silently (empty address), real deposit pool is never paused.
   ```

3. Users continue depositing into the real (unpaused) `LRTDepositPool`. The admin believes the protocol is paused. Funds remain at risk for the duration of the incident.

4. Concurrently, `updateRSETHPrice()` resolves the same empty address, gets `paused() == false`, and mints protocol fees against an incorrect TVL, corrupting the rsETH exchange rate for all depositors and withdrawers. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3)

### Citations

**File:** contracts/LRTConfig.sol (L244-251)
```text
    function _setContract(bytes32 key, address val) private {
        UtilLib.checkNonZeroAddress(val);
        if (contractMap[key] == val) {
            revert ValueAlreadyInUse();
        }
        contractMap[key] = val;
        emit SetContract(key, val);
    }
```

**File:** contracts/LRTConfig.sol (L262-285)
```text
    function pauseAll() external onlyRole(LRTConstants.PAUSER_ROLE) {
        IPausable lrtDepositPool = IPausable(getContract(LRTConstants.LRT_DEPOSIT_POOL));
        IPausable lrtWithdrawalManager = IPausable(getContract(LRTConstants.LRT_WITHDRAW_MANAGER));
        IPausable lrtOracle = IPausable(getContract(LRTConstants.LRT_ORACLE));
        IPausable rsETHContract = IPausable(rsETH);

        if (!lrtDepositPool.paused()) lrtDepositPool.pause();
        if (!lrtWithdrawalManager.paused()) lrtWithdrawalManager.pause();
        if (!lrtOracle.paused()) lrtOracle.pause();
        if (!rsETHContract.paused()) rsETHContract.pause();

        address[] memory nodeDelegatorQueue = ILRTDepositPool(address(lrtDepositPool)).getNodeDelegatorQueue();
        uint256 nodeDelegatorCount = nodeDelegatorQueue.length;

        for (uint256 i = 0; i < nodeDelegatorCount;) {
            IPausable nodeDelegator = IPausable(nodeDelegatorQueue[i]);
            if (!nodeDelegator.paused()) nodeDelegator.pause();
            unchecked {
                ++i;
            }
        }

        emit PausedAll(msg.sender);
    }
```

**File:** contracts/utils/UtilLib.sol (L10-13)
```text
    /// @param address_ address to check
    function checkNonZeroAddress(address address_) internal pure {
        if (address_ == address(0)) revert ZeroAddressNotAllowed();
    }
```

**File:** contracts/LRTOracle.sol (L236-240)
```text
        IPausable lrtDepositPool = IPausable(lrtConfig.getContract(LRTConstants.LRT_DEPOSIT_POOL));
        IPausable withdrawalManager = IPausable(lrtConfig.getContract(LRTConstants.LRT_WITHDRAW_MANAGER));

        // determine if the protocol is active (not paused)
        bool protocolPaused = lrtDepositPool.paused() || withdrawalManager.paused() || paused;
```
