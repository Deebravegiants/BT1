# [M] Lack of access control in setWorker

## Summary
Severity: Medium
Contest weight: 0.6006
Dataset id: 2672
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The lack of access control in the setWorkerPublicKey function will cause a significant loss of funds for users as a malicious actor will register a fake Worker public key to intercept and disrupt deployment payments.
In BlueprintCore.sol at the setWorkerPublicKey function, the function is declared as public without any restrictions, allowing any address to register or update a public key in the workersPublicKey mapping and add themselves to the workerAddressesMp list.
```solidity
function setWorkerPublicKey(bytes calldata publicKey) public {
    if (workersPublicKey[msg.sender].length == 0) {
        workerAddressesMp[WORKER_ADDRESS_KEY].push(msg.sender);
    }
    workersPublicKey[msg.sender] = publicKey;
}
```
Internal Pre-conditions
1. The setWorkerPublicKey function remains public and unchanged in the deployed contract.
2. Users rely on the workerAddressesMp list or getWorkerPublicKey to select Workers for private deployments (via createProjectIDAndPrivateDeploymentRequest or createAgent).
3. The createAgentWithToken function is callable, requiring payment (via payWithERC20) for agent creation linked to a Worker.
External Pre-conditions
1. The Base blockchain (per the README) allows any address to send transactions to the contract, which is standard behavior for public networks.
Attack Path
1. A malicious actor calls setWorkerPublicKey with a fake public key, registering their address in workersPublicKey and adding it to workerAddressesMp["worker_address_key"].
2. A user queries getWorkerAddresses or getWorkerPublicKey and selects the malicious actor’s address as the privateWorkerAddress for a deployment.
3. The user pays in ERC-20 tokens to create an agent, encrypting base64Proposal with the malicious Worker’s public key and triggering a deployment request.
4. The malicious actor receives the deployment request (status set to Pickup) but does not deploy the agent, either keeping the encrypted data or ignoring the request, causing the deployment to fail.
• The user suffers the loss of there ERC-20 tokens. The attacker gains no direct funds but may extract value from the encrypted base64Proposal (sensitive data), incurring only gas costs.
• Also, the transfered token will go to feeCollectionWalletAddress and protocol didn't have a functionality to refund this token to the respective users if this issue occurs. So anyway user is gonna lose their fund.

## Recommendation
• Whitelist Approach: Add a modifier to limit calls to registered Workers, managed by the owner:
```solidity
mapping(address => bool) public registeredWorkers;

modifier onlyRegisteredWorker() {
    require(registeredWorkers[msg.sender], "Not a registered Worker");
    _;
}

function setWorkerPublicKey(bytes calldata publicKey) public onlyRegisteredWorker {
    if (workersPublicKey[msg.sender].length == 0) {
        workerAddressesMp[WORKER_ADDRESS_KEY].push(msg.sender);
    }
    workersPublicKey[msg.sender] = publicKey;
}

function registerWorker(address worker) public onlyOwner {
    registeredWorkers[worker] = true;
}
```
