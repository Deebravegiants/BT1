The most direct analog to the "irremovable malicious nodes" vulnerability class in this codebase is in `PubkeyRegistry.sol`. Let me verify the complete picture before writing the finding.### Title
No Mechanism to Remove Registered Validator Pubkeys from PubkeyRegistry - (File: contracts/PubkeyRegistry.sol)

### Summary
`PubkeyRegistry` provides only append-only write functions (`addPubkey`, `addPubkeys`) with no corresponding removal function. Once a validator pubkey is registered — whether via the automated path during `stake32Eth` or via the privileged `addPubkeys` manager call — it is permanently and irrevocably marked `true` in the `pubkeyRegistry` mapping. There is no `removePubkey` or equivalent function in either the contract or its interface.

### Finding Description
`PubkeyRegistry` stores a mapping `pubkeyRegistry[keccak256(pubkey)] => bool hasBeenUsed`. The contract exposes two write paths:

1. `addPubkey(bytes calldata pubkey)` — callable only by active NodeDelegator contracts, invoked automatically inside `NodeDelegator.stake32Eth` before staking 32 ETH to a validator.
2. `addPubkeys(bytes[] calldata pubkeys)` — callable by `onlyLRTManager`, used to bulk-register pubkeys without staking ETH (e.g., for pre-registration or migration).

Neither the contract nor the `IPubkeyRegistry` interface exposes any function to set a registered pubkey back to `false` or otherwise remove it. [1](#0-0) [2](#0-1) [3](#0-2) 

The guard in `stake32Eth` that enforces uniqueness reads:

```solidity
if (pubkeyRegistry.hasPubkey(pubkey)) {
    revert PubkeyAlreadyRegistered();
}
``` [4](#0-3) 

Once a pubkey is registered — correctly or erroneously — it permanently blocks any future call to `stake32Eth` for that pubkey, with no administrative escape hatch.

### Impact Explanation
**Low — Contract fails to deliver promised returns, but doesn't lose value.**

Two concrete failure scenarios:

1. **Erroneous bulk registration via `addPubkeys`**: The LRT Manager calls `addPubkeys` with an incorrect pubkey (e.g., a typo or a pubkey belonging to a validator whose withdrawal credentials do not point to the protocol's EigenPod). That pubkey is permanently blacklisted from `stake32Eth`. The 32 ETH that was intended for that validator cannot be staked to it through the protocol. The ETH remains in the NodeDelegator and can be redirected, so no funds are lost, but the protocol fails to deliver the restaking service for that validator slot.

2. **Validator exit and re-entry**: A validator that previously staked through the protocol exits the beacon chain and fully withdraws. If the operator wishes to re-use the same BLS pubkey (e.g., re-deposit to the same validator index), the protocol permanently blocks it. The operator must use a different pubkey, which may not always be operationally possible.

No direct theft or permanent fund freeze results, placing this squarely in the Low tier.

### Likelihood Explanation
Moderate operational likelihood. The `addPubkeys` manager function is explicitly designed for bulk pre-registration without staking, making erroneous entries a realistic operational risk. Validator key re-use after exit is a known operational pattern in Ethereum staking. The absence of any removal path means any such error has permanent protocol-level consequences with no on-chain remedy.

### Recommendation
Add a `removePubkey` function restricted to a sufficiently privileged role (e.g., `onlyLRTManager` or `onlyLRTAdmin`) that sets the mapping entry back to `false`:

```solidity
function removePubkey(bytes calldata pubkey) external onlyLRTManager {
    pubkeyRegistry[keccak256(pubkey)] = false;
}
```

Also update `IPubkeyRegistry` to include this function signature. Consider whether removal should be restricted to pubkeys that were added via `addPubkeys` (i.e., not yet staked) versus all registered pubkeys, to avoid accidentally re-enabling a pubkey that is actively staked to a live validator.

### Proof of Concept

1. LRT Manager calls `addPubkeys([<validatorPubkey>])` to pre-register a pubkey. [5](#0-4) 

2. `pubkeyRegistry[keccak256(<validatorPubkey>)]` is now `true`. [1](#0-0) 

3. The manager realizes the pubkey was wrong (e.g., wrong validator, wrong withdrawal credentials).

4. There is no `removePubkey` function in `PubkeyRegistry` or `IPubkeyRegistry`. [3](#0-2) 

5. Any subsequent call to `NodeDelegator.stake32Eth` with that pubkey reverts with `PubkeyAlreadyRegistered`. [6](#0-5) 

6. The pubkey is permanently blocked. No on-chain action can undo this. The validator slot is permanently unusable through the protocol.

### Citations

**File:** contracts/PubkeyRegistry.sol (L14-14)
```text
    mapping(bytes32 pubKeyHashed => bool hasBeenUsed) public pubkeyRegistry;
```

**File:** contracts/PubkeyRegistry.sol (L41-49)
```text
    function addPubkey(bytes calldata pubkey) external onlyLRTNodeDelegator {
        pubkeyRegistry[keccak256(pubkey)] = true;
    }

    function addPubkeys(bytes[] calldata pubkeys) external onlyLRTManager {
        for (uint256 i = 0; i < pubkeys.length; i++) {
            pubkeyRegistry[keccak256(pubkeys[i])] = true;
        }
    }
```

**File:** contracts/interfaces/IPubkeyRegistry.sol (L4-9)
```text
interface IPubkeyRegistry {
    function hasPubkey(bytes calldata pubkey) external view returns (bool);

    function addPubkey(bytes calldata pubkey) external;

    function addPubkeys(bytes[] calldata pubkeys) external;
```

**File:** contracts/NodeDelegator.sol (L159-163)
```text
        IPubkeyRegistry pubkeyRegistry = IPubkeyRegistry(lrtConfig.pubkeyRegistry());
        if (pubkeyRegistry.hasPubkey(pubkey)) {
            revert PubkeyAlreadyRegistered();
        }
        pubkeyRegistry.addPubkey(pubkey);
```
