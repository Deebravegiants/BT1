### Title
`lastBridgedDepositId` Advances Past Un-Bridged Deposits via Block Stuffing — (`contracts/KERNEL/KernelVaultETH.sol`)

---

### Summary

`bridgeKernelToBSC` unconditionally sets `lastBridgedDepositId = counter - 1` at execution time, regardless of whether the `amount` parameter covers all deposits up to that counter. An attacker can use block stuffing to insert `depositKernel` calls between the operator's off-chain balance snapshot and the bridge transaction's execution, causing `lastBridgedDepositId` to advance past deposits whose KERNEL was never included in the bridged amount.

---

### Finding Description

The operator's intended workflow is:

1. Read `kernel.balanceOf(address(this))` off-chain → call it `X`, covering deposits `[lastBridgedDepositId+1 .. counter-1]`.
2. Submit `bridgeKernelToBSC(X, ...)`.

Inside `bridgeKernelToBSC`:

```solidity
// KernelVaultETH.sol line 262
lastBridgedDepositId = counter - 1;
kernelOftAdapter.send{ value: nativeFee }(sendParam, fee, refundAddress);
``` [1](#0-0) 

`lastBridgedDepositId` is assigned the **current** `counter - 1` at execution time, not the `counter - 1` that existed when the operator took their snapshot. There is no check that `amount` equals the sum of deposits from `lastBridgedDepositId + 1` to `counter - 1`.

**Block-stuffing attack sequence:**

| Step | State |
|------|-------|
| Operator snapshots balance = X; `counter = N` | Deposits `[0..N-1]` pending bridge |
| Attacker stuffs blocks (fills block gas limit with own txs) to delay operator tx | Operator tx sits in mempool |
| Attacker calls `depositKernel(Y)` → deposit `N` created; `counter = N+1` | Vault balance = X + Y |
| Operator tx executes: bridges `X`, sets `lastBridgedDepositId = counter - 1 = N` | Deposit `N` (amount Y) marked bridged; Y KERNEL still in vault |

The `_depositKernel` internal function increments `counter` on every deposit:

```solidity
// KernelVaultETH.sol lines 391-394
uint256 depositId = counter;
userDeposits[depositId] = UserDeposit({ user: user, amount: amount });
++counter;
``` [2](#0-1) 

`depositKernel` is public and permissionless:

```solidity
function depositKernel(uint256 amount) external nonReentrant whenNotPaused {
``` [3](#0-2) 

---

### Impact Explanation

`lastBridgedDepositId` is the on-chain record of which deposits have been bridged. After the attack, deposit `N` is permanently recorded as bridged (`lastBridgedDepositId = N`) while its KERNEL (`Y` tokens) remains in `KernelVaultETH`. Any off-chain system or BSC-side contract that reads `lastBridgedDepositId` from the `BridgedKernelToBSC` event to credit users will credit the attacker's deposit on BSC before the corresponding KERNEL has actually arrived. The invariant `sum(userDeposits[0..lastBridgedDepositId].amount) == total KERNEL bridged` is broken. [4](#0-3) 

---

### Likelihood Explanation

Block stuffing on Ethereum mainnet is expensive but feasible for high-value targets. More importantly, the same desync occurs **without** block stuffing in any block where a `depositKernel` call is naturally included before the operator's `bridgeKernelToBSC` call — a routine race condition. Block stuffing makes it reliable and attacker-controlled. The attacker only needs to hold enough KERNEL to meet `minDeposit` and enough ETH to fill blocks.

---

### Recommendation

Snapshot `counter` inside `bridgeKernelToBSC` and use it to set `lastBridgedDepositId`, or require the caller to pass the expected `depositIdUpperBound` and revert if `counter - 1` exceeds it:

```solidity
function bridgeKernelToBSC(
    uint256 amount,
    uint256 minAmount,
    uint256 nativeFee,
    address refundAddress,
    uint256 expectedLastDepositId   // <-- new parameter
) external payable nonReentrant onlyRole(OPERATOR_ROLE) {
    // ...
    if (counter - 1 != expectedLastDepositId) revert DepositCounterMismatch();
    lastBridgedDepositId = expectedLastDepositId;
    // ...
}
```

This makes the transaction revert (rather than silently mismatch) if any deposit lands between the snapshot and execution.

---

### Proof of Concept

```solidity
// State-sequence test (local fork or unit test)
// 1. Operator snapshots balance
uint256 snapshotBalance = kernel.balanceOf(address(vault)); // e.g. 1000e18, counter=1

// 2. Attacker deposits (simulating block stuffing inserting this before operator tx)
vm.prank(attacker);
kernel.approve(address(vault), 500e18);
vault.depositKernel(500e18); // counter becomes 2

// 3. Operator's tx executes with old snapshot amount
vm.prank(operator);
vault.bridgeKernelToBSC{value: nativeFee}(snapshotBalance, minAmount, nativeFee, refundAddress);
// lastBridgedDepositId = counter - 1 = 1  (covers attacker's deposit)
// but only 1000e18 was bridged, not 1500e18

// 4. Assert invariant is broken
uint256 sumBridged = 0;
for (uint256 i = 0; i <= vault.lastBridgedDepositId(); i++) {
    sumBridged += vault.getUserDeposit(i).amount;
}
assertEq(sumBridged, snapshotBalance); // FAILS: sumBridged = 1500e18, bridged = 1000e18
```

### Citations

**File:** contracts/KERNEL/KernelVaultETH.sol (L81-88)
```text
    event BridgedKernelToBSC(
        uint32 indexed lzChainId,
        address indexed receiver,
        uint256 amount,
        uint256 minAmount,
        uint256 nativeFee,
        uint256 lastBridgedDepositId
    );
```

**File:** contracts/KERNEL/KernelVaultETH.sol (L193-195)
```text
    function depositKernel(uint256 amount) external nonReentrant whenNotPaused {
        _depositKernel(msg.sender, amount);
    }
```

**File:** contracts/KERNEL/KernelVaultETH.sol (L262-264)
```text
        lastBridgedDepositId = counter - 1;

        kernelOftAdapter.send{ value: nativeFee }(sendParam, fee, refundAddress);
```

**File:** contracts/KERNEL/KernelVaultETH.sol (L391-394)
```text
        uint256 depositId = counter;

        userDeposits[depositId] = UserDeposit({ user: user, amount: amount });
        ++counter;
```
