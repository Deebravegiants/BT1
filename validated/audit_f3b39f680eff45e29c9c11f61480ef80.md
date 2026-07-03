### Title
`CREATE3Factory` Uses Inline-Assembly `create2` With Runtime Bytecode, Incompatible With ZKsync — (`contracts/utils/CREATE3Factory.sol` / `contracts/utils/CREATE3.sol`)

---

### Summary

The LRT-rsETH protocol explicitly supports zkSync as a deployment target (confirmed by live zkSync deployments in the README). The `CREATE3Factory` contract relies on `CREATE3.sol`, which uses inline assembly to call `create2` with bytecode passed as a runtime memory pointer. ZKsync's EVM requires the compiler to know the bytecode hash at compile time; passing bytecode via assembly at runtime bypasses this requirement, causing `create2` to silently fail or produce an incorrect result on zkSync.

---

### Finding Description

`CREATE3.sol` defines a constant proxy bytecode and deploys it via inline assembly:

```solidity
bytes internal constant PROXY_BYTECODE = hex"67363d3d37363d34f03d5260086018f3";

function deploy(bytes32 salt, bytes memory creationCode, uint256 value) internal returns (address deployed) {
    bytes memory proxyChildBytecode = PROXY_BYTECODE;
    address proxy;
    assembly {
        proxy := create2(0, add(proxyChildBytecode, 32), mload(proxyChildBytecode), salt)
    }
    require(proxy != address(0), "DEPLOYMENT_FAILED");
    ...
}
``` [1](#0-0) 

Even though `PROXY_BYTECODE` is a Solidity constant, the assembly block passes it as a raw memory pointer to `create2`. On ZKsync, `create2` does not accept raw bytecode at runtime — it requires the bytecode hash to be known to the compiler at compile time via `type(X).creationCode` or equivalent. The ZKsync compiler cannot intercept and rewrite this assembly-level `create2` call, so the deployment will fail (return `address(0)`) or revert.

`CREATE3Factory.deploy()` is the public entry point that wraps this library:

```solidity
function deploy(bytes32 salt, bytes memory creationCode) external payable returns (address deployed) {
    deployed = CREATE3.deploy(salt, creationCode, msg.value);
    emit ContractDeployed(salt, deployed);
}
``` [2](#0-1) 

---

### Impact Explanation

Any caller invoking `CREATE3Factory.deploy()` on zkSync will receive a revert (`"DEPLOYMENT_FAILED"`) because the inner `create2` returns `address(0)`. The factory cannot fulfill its core purpose — deterministic contract deployment — on zkSync. No funds are permanently lost (the call reverts), but the contract entirely fails to deliver its promised functionality on a supported chain.

**Severity: Low** — Contract fails to deliver promised returns, but doesn't lose value.

---

### Likelihood Explanation

zkSync is an explicitly supported and live chain for the LRT-rsETH protocol. [3](#0-2) 

Any attempt to use `CREATE3Factory` on zkSync — whether by the protocol team or an external caller — will fail. The likelihood is high whenever the factory is used on zkSync.

---

### Recommendation

Replace the inline-assembly `create2` with a ZKsync-compatible deployment pattern where the compiler is aware of the bytecode at compile time:

```solidity
// ZKsync-compatible pattern
bytes memory bytecode = type(ProxyContract).creationCode;
assembly {
    proxy := create2(0, add(bytecode, 32), mload(bytecode), salt)
}
```

Alternatively, use a ZKsync-native factory deployer (e.g., `IContractDeployer`) or maintain a separate ZKsync-compatible deployment path.

---

### Proof of Concept

1. Deploy `CREATE3Factory` on zkSync.
2. Call `CREATE3Factory.deploy(salt, creationCode)` with any valid `creationCode`.
3. The inner `create2` in `CREATE3.sol` line 44 returns `address(0)` because ZKsync cannot resolve the runtime-passed bytecode.
4. The `require(proxy != address(0), "DEPLOYMENT_FAILED")` at line 46 reverts the transaction.
5. No contract is deployed; the factory is non-functional on zkSync. [4](#0-3)

### Citations

**File:** contracts/utils/CREATE3.sol (L33-51)
```text
    bytes internal constant PROXY_BYTECODE = hex"67363d3d37363d34f03d5260086018f3";

    bytes32 internal constant PROXY_BYTECODE_HASH = keccak256(PROXY_BYTECODE);

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

**File:** contracts/utils/CREATE3Factory.sol (L17-20)
```text
    function deploy(bytes32 salt, bytes memory creationCode) external payable returns (address deployed) {
        deployed = CREATE3.deploy(salt, creationCode, msg.value);
        emit ContractDeployed(salt, deployed);
    }
```

**File:** README.md (L584-596)
```markdown
## zkSync
| Contract Name           |  Address                                       |
|-------------------------|------------------------------------------------|
| ProxyAdmin              |  0xd836801C07e9b471Fa3c525bc13bC4333c51F25F    |
| ProxyAdmin Owner        |  0x2Aeb356f2bE90FA2C138B044144dd9946fC63573    |
| TimelockController      |  0x2Aeb356f2bE90FA2C138B044144dd9946fC63573    |
| Timelock Proposer       |  0xeD38DA849b20Fa27B07D073053C5F5aAe6A2dB6b    |

| Contract Name           | Proxy Address                                  |
|-------------------------|------------------------------------------------|
| RsETHTokenWrapper       |  0xd4169E045bcF9a86cC00101225d9ED61D2F51af2    |
| RSETHPoolV2             |  0x41b300f5A619973b20931f0944C85DB229d5E27f    |
| HashStorage             |  0x2245AC63eA03f18D1a73BA6Ee3C4718b397fE726    |
```
