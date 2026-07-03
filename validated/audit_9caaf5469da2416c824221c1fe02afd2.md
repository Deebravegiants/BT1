Looking at the `CREATE3Factory.sol` and `CREATE3.sol` code carefully to trace the attack path.

### Title
Unguarded `deploy()` Allows Salt Griefing, Permanently Blocking Protocol's Deterministic CREATE3 Address — (`contracts/utils/CREATE3Factory.sol`)

---

### Summary

`CREATE3Factory.deploy()` has no access control and does not namespace the salt by `msg.sender`. Any caller who knows a target salt can front-run the legitimate deployer, permanently occupying the CREATE2 proxy slot for that salt and causing all subsequent legitimate `deploy()` calls with the same salt to revert with `"DEPLOYMENT_FAILED"`.

---

### Finding Description

`CREATE3Factory.deploy()` is `external payable` with no role check or caller-based salt modification: [1](#0-0) 

Internally, `CREATE3.deploy()` computes the proxy address via CREATE2 using only `address(this)` (the factory), the raw `salt`, and the fixed `PROXY_BYTECODE_HASH`: [2](#0-1) 

Because `msg.sender` is never mixed into the salt, any two callers supplying the same `salt` target the **identical** CREATE2 proxy address. If an attacker deploys first, the proxy slot is consumed. When the legitimate deployer calls `deploy()` with the same salt, `create2` returns `address(0)` (EVM rule: CREATE2 to an already-occupied address fails), and the `require` on line 46 reverts with `"DEPLOYMENT_FAILED"`. The CREATE3 child address — derived from the proxy's nonce-1 CREATE address — is now permanently occupied by the attacker's arbitrary contract: [3](#0-2) 

---

### Impact Explanation

The protocol permanently loses the ability to deploy its intended contract at the pre-announced CREATE3 address for the griefed salt. Any off-chain integrations, documentation, or cross-chain deployments that relied on that deterministic address are broken. No funds are lost, but the contract fails to deliver its core promise: a given salt always produces a deployable deterministic address for the intended caller.

**Scope:** Low — Contract fails to deliver promised returns, but doesn't lose value.

---

### Likelihood Explanation

The salt is observable from a pending mempool transaction or off-chain announcement. The attack requires only a single `deploy()` call with any valid bytecode (even a single `STOP` opcode `0x00`) and zero ETH. No special privileges are needed. The cost to the attacker is minimal gas; the damage to the protocol is permanent for that salt.

---

### Recommendation

Namespace the salt by `msg.sender` inside `CREATE3Factory.deploy()` before passing it to the library:

```solidity
function deploy(bytes32 salt, bytes memory creationCode) external payable returns (address deployed) {
    bytes32 guardedSalt = keccak256(abi.encodePacked(msg.sender, salt));
    deployed = CREATE3.deploy(guardedSalt, creationCode, msg.value);
    emit ContractDeployed(salt, deployed);
}
```

This ensures each caller has an exclusive namespace, making salt griefing impossible. `getDeployed` should be updated similarly to accept a `deployer` parameter for off-chain address prediction.

---

### Proof of Concept

```solidity
// SPDX-License-Identifier: MIT
pragma solidity 0.8.27;

import "forge-std/Test.sol";
import "contracts/utils/CREATE3Factory.sol";

contract CREATE3FrontRunTest is Test {
    CREATE3Factory factory;

    function setUp() public {
        factory = new CREATE3Factory();
    }

    function test_saltGriefing() public {
        bytes32 salt = keccak256("rsETH_LRTDepositPool_v1");

        // Attacker front-runs with dummy bytecode (single STOP opcode)
        address attacker = makeAddr("attacker");
        vm.prank(attacker);
        factory.deploy(salt, hex"00");

        // Legitimate deployer attempts to deploy real contract
        address legitDeployer = makeAddr("legitDeployer");
        bytes memory realCode = type(CREATE3Factory).creationCode; // any real bytecode
        vm.prank(legitDeployer);
        vm.expectRevert("DEPLOYMENT_FAILED");
        factory.deploy(salt, realCode);

        // The CREATE3 address is permanently occupied by attacker's dummy contract
        address occupied = factory.getDeployed(salt);
        assertGt(occupied.code.length, 0, "attacker contract occupies the address");
    }
}
```

### Citations

**File:** contracts/utils/CREATE3Factory.sol (L17-19)
```text
    function deploy(bytes32 salt, bytes memory creationCode) external payable returns (address deployed) {
        deployed = CREATE3.deploy(salt, creationCode, msg.value);
        emit ContractDeployed(salt, deployed);
```

**File:** contracts/utils/CREATE3.sol (L41-46)
```text
        assembly {
            // Deploy a new contract with our pre-made bytecode via CREATE2.
            // We start 32 bytes into the code to avoid copying the byte length.
            proxy := create2(0, add(proxyChildBytecode, 32), mload(proxyChildBytecode), salt)
        }
        require(proxy != address(0), "DEPLOYMENT_FAILED");
```

**File:** contracts/utils/CREATE3.sol (L53-65)
```text
    function getDeployed(bytes32 salt) internal view returns (address) {
        address proxy = keccak256(abi.encodePacked(bytes1(0xFF), address(this), salt, PROXY_BYTECODE_HASH)).
            // Prefix:
            // Creator:
            // Salt:
            // Bytecode hash:
            fromLast20Bytes();

        return keccak256(abi.encodePacked(hex"d694", proxy, hex"01")) // Nonce of the proxy contract (1)
            // 0xd6 = 0xc0 (short RLP prefix) + 0x16 (length of: 0x94 ++ proxy ++ 0x01)
            // 0x94 = 0x80 + 0x14 (0x14 = the length of an address, 20 bytes, in hex)
            .fromLast20Bytes();
    }
```
