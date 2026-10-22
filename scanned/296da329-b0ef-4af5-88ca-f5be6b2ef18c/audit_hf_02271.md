# [M] Minimum Delay Bypass In TimelockController

## Summary
Severity: Medium
Contest weight: 0.4606
Dataset id: 12447
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The TimelockController, introduced in OpenZeppelin Contracts 3.3, is a smart contract that enforces a delay on all actions directed towards an owned contract.
A typical setup is to position the TimelockController as the admin of an application smart contract such that, whenever a privileged action is to be executed, it has to wait for a certain time speciﬁed by the TimelockController.
The security beneﬁts of the TimelockController are twofold. Firstly, it provides an extra layer of security to a project's team by giving a heads up on every privileged action anticipated in the system. This allows the team to detect and react to malicious calls by compromised admin accounts.
Secondly, it protects the community from the project's governance itself, allowing members to exit the protocol if they disagree with any impending changes.
In particular, scheduleBatch() (a schedule function) and executeBatch() (an execute function), allow the caller to enqueue and execute proposals that run multiple calls in sequence. However, there is a vulnerability in their implementation that can be exploited by the malicious EXECUTOR to execute arbitrary tasks bypassing the minimum delay protection.
To elaborate, we show below the related code snippet of the TimelockController contract. A malicious EXECUTOR could execute a batch with the calling of executeBatch(), including a set of calls, i.e., the call to the TimelockController itself to clear the minimum delay and grant PROPOSER and ADMIN rights to an address under their control, the call to scheduleBatch() to enqueue the batch by the controlled PROPOSER and the call to the arbitrary privileged functions under the TimelockController control. By doing so, the malicious EXECUTOR eﬀectively takes full control of the TimelockController contract.
```solidity
function executeBatch(
    address[] calldata targets,
    uint256[] calldata values,
    bytes[] calldata datas,
    bytes32 predecessor,
    bytes32 salt
) external payable virtual onlyRole(EXECUTOR_ROLE) {
    require(
        targets.length == values.length,
        "TimelockController: length mismatch"
    );
    require(
        targets.length == datas.length,
        "TimelockController: length mismatch"
    );
    bytes32 id = hashOperationBatch(targets, values, datas, predecessor, salt);
    _beforeCall(predecessor);
    for (uint256 i = 0; i < targets.length; ++i) {
        _call(id, i, targets[i], values[i], datas[i]);
    }
    _afterCall(id);
}

function scheduleBatch(
    address[] calldata targets,
    uint256[] calldata values,
    bytes[] calldata datas,
    bytes32 predecessor,
    bytes32 salt,
    uint256 delay
) external virtual onlyRole(PROPOSER_ROLE) {
    require(
        targets.length == values.length,
        "TimelockController: length mismatch"
    );
    require(
        targets.length == datas.length,
        "TimelockController: length mismatch"
    );
    bytes32 id = hashOperationBatch(targets, values, datas, predecessor, salt);
    _schedule(id, delay);
    for (uint256 i = 0; i < targets.length; ++i) {
        emit CallScheduled(
            id,
            i,
            targets[i],
            values[i],
            datas[i],
            predecessor,
            delay
        );
    }
}
```

## Recommendation
Considering the OpenZeppelin team has solved this vulnerability, we suggest to upgrade the TimelockController to the latest version.
