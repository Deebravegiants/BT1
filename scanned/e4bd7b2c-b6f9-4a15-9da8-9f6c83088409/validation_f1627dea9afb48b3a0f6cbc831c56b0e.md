### Title
`CREATE3Factory.deploy`: Predictable Deployment Address Enables Front-Running DoS and Fund Theft — (File: `contracts/utils/CREATE3Factory.sol`)

---

### Summary

`CREATE3Factory.deploy` accepts a caller-supplied `salt` and passes it directly to `CREATE3.deploy` without incorporating `msg.sender`. Because the deployed address is deterministic from `(factory_address, salt)` alone, any observer of the public mempool can front-run a pending deployment with the same salt, causing the victim's transaction to revert and potentially stealing ETH sent alongside the deployment.

---

### Finding Description

`CREATE3Factory.deploy` is a permissionless, `external payable` function:

```solidity
function deploy(bytes32 salt, bytes memory creationCode) external payable returns (address deployed) {
    deployed = CREATE3.deploy(salt, creationCode, msg.value);
    emit ContractDeployed(salt, deployed);
}
``` [1](#0-0) 

Internally, `CREATE3.deploy` uses the raw `salt` in a `CREATE2` call to deploy a proxy:

```solidity
proxy := create2(0, add(proxyChildBytecode, 32), mload(proxyChildBytecode), salt)
``` [2](#0-1) 

And `CREATE3.getDeployed` computes the final address from only `address(this)` and `salt`:

```solidity
address proxy = keccak256(abi.encodePacked(bytes1(0xFF), address(this), salt, PROXY_BYTECODE_HASH))
    .fromLast20Bytes();
``` [3](#0-2) 

Because `msg.sender` is never mixed into the salt, the target address for any `(factory, salt)` pair is globally predictable and claimable by anyone. The `getDeployed` view function makes this trivial to compute off-chain. [4](#0-3) 

---

### Impact Explanation

**DoS (Medium — Temporary Freezing of Funds / Deployment Capability):**
An attacker watching the mempool sees a pending `deploy(salt, creationCode)` call. They submit the same `salt` with higher gas. The proxy is deployed at the deterministic address. When the victim's transaction executes, `create2` returns `address(0)` (proxy already exists), and the `require(proxy != address(0), "DEPLOYMENT_FAILED")` reverts the entire call. The victim cannot deploy to their intended address with that salt.

**Fund Theft (Critical — if ETH accompanies deployment):**
If the victim sends `msg.value > 0` with their `deploy` call (to fund the newly deployed contract), the attacker can front-run with the same salt and a malicious `creationCode`. The attacker's contract is deployed at the predicted address. The victim's transaction reverts and their ETH is returned in that transaction, but if the victim (or any protocol component) subsequently sends ETH to the predicted address — believing their own contract resides there — the attacker's contract receives and can drain those funds.

---

### Likelihood Explanation

- `CREATE3Factory.deploy` is `external` with no access control — any address can call it.
- The `salt` is visible in the public mempool before the transaction is mined.
- `getDeployed(salt)` is a public view function that makes address prediction trivial.
- Front-running is straightforward on any chain where the factory is deployed (including L2s where the factory comment notes it is intended to be deployed at the same address across chains). [5](#0-4) 

---

### Recommendation

Incorporate `msg.sender` into the salt before passing it to `CREATE3.deploy`, mirroring the fix applied in the referenced Caviar report:

```solidity
function deploy(bytes32 salt, bytes memory creationCode) external payable returns (address deployed) {
    bytes32 guardedSalt = keccak256(abi.encode(msg.sender, salt));
    deployed = CREATE3.deploy(guardedSalt, creationCode, msg.value);
    emit ContractDeployed(salt, deployed);
}
```

Update `getDeployed` accordingly to accept a `deployer` address parameter so callers can still predict their own deployment addresses:

```solidity
function getDeployed(address deployer, bytes32 salt) external view returns (address) {
    return CREATE3.getDeployed(keccak256(abi.encode(deployer, salt)));
}
```

---

### Proof of Concept

1. Victim broadcasts `CREATE3Factory.deploy(salt_X, creationCode, 1 ether)`.
2. Attacker observes the pending transaction in the mempool.
3. Attacker calls `CREATE3Factory.deploy(salt_X, maliciousCode)` with higher gas priority.
4. Attacker's proxy is deployed via `create2` at the address determined by `(factory, salt_X)`.
5. Victim's transaction executes: `create2` returns `address(0)` (proxy already exists); `require` reverts; victim's 1 ETH is returned.
6. Any subsequent protocol action that sends ETH to `getDeployed(salt_X)` — the address the victim expected to own — instead funds the attacker's malicious contract.
7. Attacker withdraws the ETH from their malicious contract. [6](#0-5)

### Citations

**File:** contracts/utils/CREATE3Factory.sol (L8-8)
```text
/// @dev This factory can be deployed at the same address on multiple chains
```

**File:** contracts/utils/CREATE3Factory.sol (L17-19)
```text
    function deploy(bytes32 salt, bytes memory creationCode) external payable returns (address deployed) {
        deployed = CREATE3.deploy(salt, creationCode, msg.value);
        emit ContractDeployed(salt, deployed);
```

**File:** contracts/utils/CREATE3Factory.sol (L25-27)
```text
    function getDeployed(bytes32 salt) external view returns (address) {
        return CREATE3.getDeployed(salt);
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

**File:** contracts/utils/CREATE3.sol (L54-59)
```text
        address proxy = keccak256(abi.encodePacked(bytes1(0xFF), address(this), salt, PROXY_BYTECODE_HASH)).
            // Prefix:
            // Creator:
            // Salt:
            // Bytecode hash:
            fromLast20Bytes();
```
