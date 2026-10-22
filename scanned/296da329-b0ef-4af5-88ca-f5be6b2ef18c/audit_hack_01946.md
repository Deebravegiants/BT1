# [H] 6.1 OperationStorage Can Be Polluted

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Security High Version 1 Code Corrected


OperationStorage is designed to be used as a temporary store of actions and return values for the
execution of an operation. Therefore, the variables it contains are deleted at the end of every operation
execution. However, as it lacks access control, and since there is no mechanism to ensure that
OperationStorage is empty before an execution, action and return values could be maliciously or
erroneously introduced.

In particular, an attacker could store spurious return values with the push function. In the next execution
actions may retrieve these values instead of the intended ones which are appended at the end of the
array.

Finally, it should be considered that the execution of actions may reach untrusted code (integrations,
tokens). Functions push and finalize may be accessed unexpectedly even within the execution of an
action. This similarly applies to functions setOperationActions and verifyAction were it is not
obvious whether this can have a negative impact.

Code partially corrected:

OperationStorage is now cleared at the beginning of OperationExecutor.executeOp(), this
ensures that the execution of operation does not start with a polluted OperationStorage which mitigates
the main issue.

Within execution of actions untrusted code may be reached (integrations, tokens), in theory they may
execute state changing functions of the OperationStorage: push(), verifyAction(),
clearStorageAfter().

Code corrected:

OperationStorage contract now stores the return values from actions in a mapping where values are
assigned to the address that pushed them.

```
mapping(address => bytes32[]) public returnValues;
```
```
function push(bytes32 value) external {
...
returnValues[msg.sender].push(value);
}
```
```
function at(uint256 index, address who) external view returns (bytes32) {
return returnValues[who][index];
}
```
When writing to the OperationStorage, an address can only write in the array associated to this address.
When reading from the OperationStorage, the caller must specify which value from which address he
wants to read. This prevents untrusted code to tamper with the return values during an operation.

In case of a flashloan action executed from the AutomationBot (more precicesly a Flashloan action with
flag dsProxyFlashloan set to false) execution continues in the context of the OperationExecutor.
The original initiator will be pushed to the OperationStorage, when called from the OperationExecutor
functions push, at and len will use this address instead of msg.sender.
