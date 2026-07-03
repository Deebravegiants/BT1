### Title
Hardcoded Proxy Nonce `0x01` in CREATE3 Address Derivation Breaks Deployment on zkSync Era - (File: contracts/utils/CREATE3.sol)

### Summary
`CREATE3.getDeployed()` hardcodes the proxy contract's nonce as `hex"01"` when computing the child contract address. On zkSync Era, newly deployed contracts start with a deployment nonce of `0`, not `1` as EIP-161 mandates. This causes `CREATE3Factory.deploy()` to always revert on zkSync Era with `"INITIALIZATION_FAILED"`, making the factory completely non-functional on that chain.

### Finding Description
In `contracts/utils/CREATE3.sol`, the `getDeployed()` function computes the deterministic address of the child contract by RLP-encoding the proxy address and its expected nonce:

```solidity
return keccak256(abi.encodePacked(hex"d694", proxy, hex"01")) // Nonce of the proxy contract (1)
``` [1](#0-0) 

The `hex"01"` encodes the assumption that the proxy's deployment nonce is `1` at the time it executes `CREATE` to deploy the child — consistent with EIP-161, which requires the nonce to be incremented to `1` before the constructor runs.

On zkSync Era, this increment does not happen. The proxy's deployment nonce remains `0` when it executes `CREATE`, so the actual child contract lands at the address derived from nonce `0`, not nonce `1`.

In `deploy()`, the predicted address is captured before the proxy call:

```solidity
deployed = getDeployed(salt);
(bool success,) = proxy.call{ value: value }(creationCode);
require(success && deployed.code.length != 0, "INITIALIZATION_FAILED");
``` [2](#0-1) 

Because `deployed` points to the nonce-1 address while the actual contract was placed at the nonce-0 address, `deployed.code.length` is always `0` on zkSync Era, and every call to `CREATE3Factory.deploy()` reverts.

`CREATE3Factory` is explicitly designed for cross-chain deterministic deployment ("This factory can be deployed at the same address on multiple chains"): [3](#0-2) 

### Impact Explanation
Any caller invoking `CREATE3Factory.deploy()` on zkSync Era will have their transaction revert unconditionally. The factory is entirely non-functional on that chain. No funds are permanently lost (the revert returns any `msg.value`), but the contract fails to deliver its core promised functionality — deterministic cross-chain deployment.

**Impact: Low** — Contract fails to deliver promised returns, but does not lose value.

### Likelihood Explanation
The `CREATE3Factory.deploy()` function is `external payable` with no access control, callable by any user. The factory's stated purpose is multi-chain deployment at a consistent address. Any attempt to use it on zkSync Era triggers the bug on the very first call. Likelihood is high given the cross-chain intent.

### Recommendation
Replace the hardcoded `hex"01"` nonce with a conditional that accounts for zkSync Era's nonce-0 behavior, or document that the factory is incompatible with zkSync Era. A portable fix uses nonce `0x00` on zkSync and `0x01` on EVM:

```solidity
// On zkSync Era, proxy deployment nonce starts at 0
bytes memory nonceEncoding = isZkSync ? abi.encodePacked(hex"d694", proxy, hex"80") // nonce=0 RLP
                                       : abi.encodePacked(hex"d694", proxy, hex"01"); // nonce=1 RLP
return keccak256(nonceEncoding).fromLast20Bytes();
```

Alternatively, adopt a zkSync-aware CREATE3 library that handles both cases.

### Proof of Concept
1. Deploy `CREATE3Factory` on zkSync Era.
2. Call `deploy(salt, creationCode)` with any valid `creationCode`.
3. Internally, `CREATE2` deploys the proxy successfully.
4. The proxy executes `CREATE` and deploys the child at address `A` (derived from nonce `0`).
5. `getDeployed(salt)` returns address `B` (derived from nonce `1`, `B ≠ A`).
6. `require(success && deployed.code.length != 0)` fails because `B.code.length == 0`.
7. Transaction reverts with `"INITIALIZATION_FAILED"` — factory is permanently broken on zkSync Era. [4](#0-3) [5](#0-4)

### Citations

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

**File:** contracts/utils/CREATE3.sol (L61-64)
```text
        return keccak256(abi.encodePacked(hex"d694", proxy, hex"01")) // Nonce of the proxy contract (1)
            // 0xd6 = 0xc0 (short RLP prefix) + 0x16 (length of: 0x94 ++ proxy ++ 0x01)
            // 0x94 = 0x80 + 0x14 (0x14 = the length of an address, 20 bytes, in hex)
            .fromLast20Bytes();
```

**File:** contracts/utils/CREATE3Factory.sol (L8-20)
```text
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
```
