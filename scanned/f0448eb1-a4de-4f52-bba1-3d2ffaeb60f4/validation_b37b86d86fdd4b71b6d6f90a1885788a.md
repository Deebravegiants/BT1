### Title
Missing Deposit Root Validation in `stake32Eth` Allows Front-Running to Steal 32 ETH Per Validator - (File: contracts/NodeDelegator.sol)

### Summary
`NodeDelegator.stake32Eth` is a `public` function callable by the LRT operator that submits a 32 ETH validator deposit to the ETH2.0 deposit contract without verifying the current deposit root. A parallel safe variant, `stake32EthValidated`, exists and performs this check, but `stake32Eth` remains directly callable. An attacker who observes the operator's pending `stake32Eth` transaction in the mempool can front-run it by depositing to the ETH2.0 deposit contract under the same pubkey, causing the protocol's 32 ETH to be credited to the attacker's validator with the attacker's withdrawal credentials.

### Finding Description
`NodeDelegator.sol` exposes two staking entry points:

**`stake32Eth`** — `public`, `onlyLRTOperator`, no deposit root check: [1](#0-0) 

**`stake32EthValidated`** — `external`, no access control modifier, performs deposit root check before delegating to `stake32Eth`: [2](#0-1) 

Because `stake32Eth` is `public` and carries no deposit root guard, the operator can invoke it directly. When the operator's `stake32Eth` transaction is in the mempool, an attacker can:

1. Extract the `pubkey` from the pending transaction.
2. Submit their own initial deposit to the ETH2.0 deposit contract (`IETHPOSDeposit.deposit`) for that same `pubkey` with the attacker's own withdrawal credentials, paying the minimum 1 ETH.
3. The attacker's transaction is mined first, registering the pubkey with the attacker's withdrawal credentials.
4. The operator's `stake32Eth` call is then mined; the ETH2.0 deposit contract treats it as a top-up of the attacker's existing validator entry, ignoring the protocol's withdrawal credentials.
5. The 32 ETH is permanently credited to the attacker's beacon chain validator.

The ETH2.0 deposit contract interface confirms `get_deposit_root()` is available for exactly this guard: [3](#0-2) 

### Impact Explanation
Each call to `stake32Eth` that is front-run results in a permanent, irrecoverable loss of 32 ETH from the protocol. The funds are credited to the attacker's beacon chain validator and cannot be recovered by the protocol. This is a direct theft of user funds at-rest, qualifying as **Critical**.

### Likelihood Explanation
The operator is expected to call `stake32Eth` regularly to onboard validators. The function is `public` and its calldata (including the target pubkey) is visible in the mempool before inclusion. The attacker only needs to submit a competing ETH2.0 deposit with a small ETH amount and the same pubkey. No special privileges are required of the attacker. The attack is straightforward and repeatable for every validator the operator attempts to register via `stake32Eth`.

### Recommendation
Remove the `public` `stake32Eth` function or restrict it so it can only be called internally by `stake32EthValidated`. Alternatively, merge the deposit root check directly into `stake32Eth` and deprecate the unguarded variant:

```solidity
function stake32Eth(
    bytes calldata pubkey,
    bytes calldata signature,
    bytes32 depositDataRoot,
    bytes32 expectedDepositRoot   // add this
)
    public
    whenNotPaused
    onlyLRTOperator
{
    IETHPOSDeposit depositContract = _getEigenPodManager().ethPOS();
    bytes32 actualDepositRoot = depositContract.get_deposit_root();
    if (expectedDepositRoot != actualDepositRoot) {
        revert InvalidDepositRoot(expectedDepositRoot, actualDepositRoot);
    }
    // ... rest of logic
}
```

The `expectedDepositRoot` must be computed off-chain at a point in time when no prior deposit for the target pubkey exists, matching the pattern already implemented in `stake32EthValidated`. [4](#0-3) 

### Proof of Concept

1. Operator constructs a `stake32Eth(pubkey, sig, depositDataRoot)` transaction and broadcasts it.
2. Attacker monitors the mempool, extracts `pubkey`.
3. Attacker calls `IETHPOSDeposit.deposit(pubkey, attacker_withdrawal_creds, attacker_sig, attacker_deposit_data_root)` with 1 ETH and a higher gas price, front-running the operator.
4. Attacker's transaction is mined first; the ETH2.0 deposit contract records the pubkey with the attacker's withdrawal credentials.
5. Operator's `stake32Eth` is mined; `_getEigenPodManager().stake{ value: 32 ether }(pubkey, signature, depositDataRoot)` is called. [5](#0-4) 
6. The ETH2.0 deposit contract treats this as a top-up of the attacker's validator. The protocol's withdrawal credentials are ignored.
7. 32 ETH is permanently lost to the protocol; `stakedButUnverifiedNativeETH` is incremented by 32 ETH but the ETH is unrecoverable. [6](#0-5)

### Citations

**File:** contracts/NodeDelegator.sol (L150-168)
```text
    function stake32Eth(
        bytes calldata pubkey,
        bytes calldata signature,
        bytes32 depositDataRoot
    )
        public
        whenNotPaused
        onlyLRTOperator
    {
        IPubkeyRegistry pubkeyRegistry = IPubkeyRegistry(lrtConfig.pubkeyRegistry());
        if (pubkeyRegistry.hasPubkey(pubkey)) {
            revert PubkeyAlreadyRegistered();
        }
        pubkeyRegistry.addPubkey(pubkey);

        // tracks staked but unverified native ETH
        stakedButUnverifiedNativeETH += 32 ether;

        _getEigenPodManager().stake{ value: 32 ether }(pubkey, signature, depositDataRoot);
```

**File:** contracts/NodeDelegator.sol (L186-199)
```text
    function stake32EthValidated(
        bytes calldata pubkey,
        bytes calldata signature,
        bytes32 depositDataRoot,
        bytes32 expectedDepositRoot
    )
        external
    {
        IETHPOSDeposit depositContract = _getEigenPodManager().ethPOS();
        bytes32 actualDepositRoot = depositContract.get_deposit_root();
        if (expectedDepositRoot != actualDepositRoot) {
            revert InvalidDepositRoot(expectedDepositRoot, actualDepositRoot);
        }
        stake32Eth(pubkey, signature, depositDataRoot);
```

**File:** contracts/external/eigenlayer/interfaces/IETHPOSDeposit.sol (L36-38)
```text
    /// @notice Query the current deposit root hash.
    /// @return The deposit root hash.
    function get_deposit_root() external view returns (bytes32);
```
