### Title
Unrestricted Salt in `CREATE3Factory.deploy()` Enables Reorg-Based Fund Theft - (File: contracts/utils/CREATE3Factory.sol)

### Summary

`CREATE3Factory.deploy()` accepts a caller-supplied `bytes32 salt` without binding it to `msg.sender`. Because the deployed address is deterministic from `(factory_address, salt)` alone, any unprivileged caller can deploy a contract they control at any pre-computed address. During a block reorg, an attacker can front-run a legitimate deployer, placing a malicious contract at the address to which the victim already sent funds.

### Finding Description

`CREATE3Factory` is a permissionless, publicly callable factory designed to deploy contracts at deterministic addresses across multiple EVM chains. [1](#0-0) 

The `deploy` function passes the raw caller-supplied `salt` directly to `CREATE3.deploy`: [2](#0-1) 

Inside `CREATE3.deploy`, the proxy is deployed via `create2` using that salt verbatim, and the final contract address is derived from the proxy's nonce-1 `CREATE` output: [3](#0-2) 

The final deployed address is therefore a pure function of `(factory_address, salt)` — `msg.sender` is never mixed in. There is no access control on `deploy`; any external account can call it with any salt. [4](#0-3) 

**Exploit flow (reorg scenario):**

1. Alice uses `getDeployed(saltX)` to pre-compute the deterministic address `addrX` for her intended deployment.
2. Alice sends ETH or ERC-20 tokens to `addrX` in anticipation of her deployment (counterfactual funding, a standard pattern for cross-chain deployments).
3. Alice submits `deploy(saltX, legitimateCreationCode)`.
4. A block reorg occurs (common on Arbitrum, Polygon, Optimism) that removes Alice's `deploy` transaction but keeps her fund-transfer transaction.
5. Bob observes the reorg and immediately calls `deploy(saltX, maliciousCreationCode)` — a contract he controls — using the same `saltX`.
6. Bob's contract is deployed at `addrX` (same deterministic address).
7. Alice's fund-transfer is re-executed, sending funds into Bob's contract.
8. Bob calls a drain function on his contract and steals Alice's funds.

The `CREATE3Factory` comment explicitly states it is designed to be deployed at the same address on multiple chains, making cross-chain counterfactual funding a primary intended use case and therefore a realistic trigger for this attack. [5](#0-4) 

### Impact Explanation

An attacker can deploy an arbitrary contract at any pre-computed `CREATE3` address by supplying the same salt as a legitimate deployer during a reorg window. Any ETH or tokens sent to that address before deployment are permanently transferred to the attacker's contract. This constitutes **direct theft of user funds** — Critical severity.

### Likelihood Explanation

- The factory is permissionless (`external`, no access control).
- The protocol targets multi-chain deployment including Arbitrum and other L2s that are historically susceptible to reorgs.
- Counterfactual funding (sending assets to a pre-computed address before deployment) is the primary design motivation for CREATE3 cross-chain factories, making this a realistic user behavior.
- The attacker only needs to monitor the mempool/reorg events and submit one transaction — no privileged access required.

### Recommendation

Bind the salt to `msg.sender` inside `deploy` before passing it to `CREATE3.deploy`:

```solidity
function deploy(bytes32 salt, bytes memory creationCode) external payable returns (address deployed) {
    bytes32 guardedSalt = keccak256(abi.encodePacked(msg.sender, salt));
    deployed = CREATE3.deploy(guardedSalt, creationCode, msg.value);
    emit ContractDeployed(salt, deployed);
}
```

Update `getDeployed` similarly so callers can still pre-compute their address:

```solidity
function getDeployed(bytes32 salt) external view returns (address) {
    bytes32 guardedSalt = keccak256(abi.encodePacked(msg.sender, salt));
    return CREATE3.getDeployed(guardedSalt);
}
```

This ensures no two callers can ever claim the same final address, eliminating the reorg front-running vector.

### Proof of Concept

1. Deploy `CREATE3Factory` on a reorg-susceptible chain (Arbitrum, Polygon).
2. Alice calls `getDeployed(saltX)` → receives `addrX`.
3. Alice sends 10 ETH to `addrX`.
4. Alice submits `deploy(saltX, legitimateCode)` — transaction lands in block N.
5. Block N is reorged out; Alice's ETH transfer is re-included but her `deploy` is dropped.
6. Bob calls `deploy(saltX, attackerCode)` where `attackerCode` is a contract with a `drain()` function sending all ETH to Bob.
7. Bob's contract is deployed at `addrX` (same salt → same address).
8. Alice's ETH transfer re-executes, crediting `addrX` (Bob's contract) with 10 ETH.
9. Bob calls `drain()` → receives 10 ETH. [1](#0-0) [3](#0-2)

### Citations

**File:** contracts/utils/CREATE3Factory.sol (L8-8)
```text
/// @dev This factory can be deployed at the same address on multiple chains
```

**File:** contracts/utils/CREATE3Factory.sol (L17-20)
```text
    function deploy(bytes32 salt, bytes memory creationCode) external payable returns (address deployed) {
        deployed = CREATE3.deploy(salt, creationCode, msg.value);
        emit ContractDeployed(salt, deployed);
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
