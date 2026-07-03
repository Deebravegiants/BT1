### Title
DoS: Attacker May Front-Run `CREATE3Factory.deploy()` With The Same `salt`, Permanently Blocking Deterministic Address Deployment - (File: contracts/utils/CREATE3Factory.sol)

### Summary
`CREATE3Factory.deploy()` is a fully permissionless `external payable` function with no access control. Any caller can supply any `salt` and any `creationCode`. Because CREATE3 internally uses CREATE2 for the proxy step, a given `salt` can only be consumed once per factory address. An attacker who observes a pending deployment transaction in the mempool can front-run it with the same `salt` but arbitrary `creationCode`, permanently consuming the salt and deploying a contract of the attacker's choosing at the deterministic address the protocol intended to use.

### Finding Description
`CREATE3Factory` is explicitly designed to deploy protocol contracts at the **same deterministic address on multiple chains** — this is its stated purpose. [1](#0-0) 

The `deploy()` function passes the caller-supplied `salt` directly to `CREATE3.deploy()`: [2](#0-1) 

Inside `CREATE3.deploy()`, the salt is used verbatim in a `create2` opcode to deploy a proxy: [3](#0-2) 

Once the proxy is deployed at `keccak256(0xFF, factory, salt, PROXY_BYTECODE_HASH)`, that CREATE2 slot is permanently occupied. Any subsequent call with the same `salt` will produce `proxy == address(0)` and revert with `"DEPLOYMENT_FAILED"`. [4](#0-3) 

There is no `onlyOwner`, `onlyRole`, or any other guard on `deploy()`. Any EOA or contract can call it with any `salt` and any `creationCode`.

### Impact Explanation
**Medium — Temporary/permanent freezing of protocol deployment operations and potential deployment of a malicious contract at the expected address.**

1. **Salt permanently consumed**: The protocol can never deploy to the intended deterministic address using that salt again. Since the entire value of CREATE3 is cross-chain address consistency, this breaks the protocol's deployment invariant.
2. **Malicious contract at expected address**: The attacker can supply arbitrary `creationCode`, deploying a contract they control at the address the protocol expected to own. If any other on-chain component (bridge receiver, oracle, pool) is pre-configured to trust that deterministic address, the attacker's contract sits at that trusted address.
3. **Attack is repeatable**: Every time the protocol attempts a new salt, the attacker can front-run again.

### Likelihood Explanation
**Medium.** The `CREATE3Factory` is used for protocol infrastructure deployments (bridges, wrappers, oracles, pools) visible in the README across many chains. Deployment transactions are visible in the public mempool on all EVM chains where this factory is deployed. The attack requires only a higher gas bid and knowledge of the pending salt — no special privileges or capital.

### Recommendation
Add access control to `CREATE3Factory.deploy()` so only authorized deployers (e.g., a multisig or timelock) can call it:

```solidity
import { Ownable } from "@openzeppelin/contracts/access/Ownable.sol";

contract CREATE3Factory is Ownable {
    function deploy(bytes32 salt, bytes memory creationCode)
        external payable onlyOwner returns (address deployed)
    {
        deployed = CREATE3.deploy(salt, creationCode, msg.value);
        emit ContractDeployed(salt, deployed);
    }
}
```

Alternatively, bind the salt to `msg.sender` so each caller has an isolated salt namespace:

```solidity
bytes32 boundSalt = keccak256(abi.encode(msg.sender, salt));
deployed = CREATE3.deploy(boundSalt, creationCode, msg.value);
```

### Proof of Concept

1. Protocol team broadcasts a transaction:
   `CREATE3Factory.deploy(keccak256("rsETH_bridge_v2"), legitimateCreationCode)`
2. Attacker sees the pending transaction in the mempool, extracts the `salt`.
3. Attacker submits `CREATE3Factory.deploy(keccak256("rsETH_bridge_v2"), maliciousCreationCode)` with a higher gas price.
4. Attacker's transaction is mined first. `CREATE3.deploy()` succeeds: the proxy is deployed via CREATE2 at the deterministic slot, and the attacker's `maliciousCreationCode` is executed through it, placing an attacker-controlled contract at the expected address.
5. Protocol's original transaction is mined next. `create2(...)` returns `address(0)` because the proxy slot is already occupied. The call reverts with `"DEPLOYMENT_FAILED"`.
6. The salt `keccak256("rsETH_bridge_v2")` is permanently consumed. The protocol cannot deploy to that address on this chain, breaking cross-chain address parity. Any protocol component pre-configured to trust that address now points to the attacker's contract. [5](#0-4) [6](#0-5)

### Citations

**File:** contracts/utils/CREATE3Factory.sol (L1-28)
```text
// SPDX-License-Identifier: MIT
pragma solidity 0.8.27;

import { CREATE3 } from "./CREATE3.sol";

/// @title CREATE3Factory
/// @notice Factory contract for deploying contracts using CREATE3
/// @dev This factory can be deployed at the same address on multiple chains
contract CREATE3Factory {
    /// @notice Emitted when a contract is deployed
    event ContractDeployed(bytes32 indexed salt, address indexed deployedAddress);

    /// @notice Deploy a contract using CREATE3
    /// @param salt The salt for deterministic address generation
    /// @param creationCode The contract creation code with constructor parameters
    /// @return deployed The address of the deployed contract
    function deploy(bytes32 salt, bytes memory creationCode) external payable returns (address deployed) {
        deployed = CREATE3.deploy(salt, creationCode, msg.value);
        emit ContractDeployed(salt, deployed);
    }

    /// @notice Get the deployed address for a given salt
    /// @param salt The salt used for deployment
    /// @return The deterministic address
    function getDeployed(bytes32 salt) external view returns (address) {
        return CREATE3.getDeployed(salt);
    }
}
```

**File:** contracts/utils/CREATE3.sol (L37-51)
```text
    function deploy(bytes32 salt, bytes memory creationCode, uint256 value) internal returns (address deployed) {
        bytes memory proxyChildBytecode = PROXY_BYTECODE;

        address proxy;
        assembly {
            // Deploy a new contract with our pre-made bytecode via CREATE2.
            // We start 32 bytes into the code to avoid copying the byte length.
            proxy := create2(0, add(proxyChildBytecode, 32), mload(proxyChildBytecode), salt)
        }
        require(proxy != address(0), "DEPLOYMENT_FAILED");

        deployed = getDeployed(salt);
        (bool success,) = proxy.call{ value: value }(creationCode);
        require(success && deployed.code.length != 0, "INITIALIZATION_FAILED");
    }
```
