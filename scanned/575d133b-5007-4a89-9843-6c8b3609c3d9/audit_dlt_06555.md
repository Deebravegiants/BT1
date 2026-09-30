# [H] Potential Vulnerability in `execTransactionOnBehalf` Function Allowing Destruction of `targetSafe` contract

## Summary
Severity: High
Chain: Smart contract
Component: Palmera
Published: 2024-06-27
Source: https://github.com/hats-finance/Palmera-0x5fee7541ddcd51ba9f4af606f87b2c42eea655be/issues/61
Type: hats-finding

## Details
**Github username:** --
**Twitter username:** --
**Submission hash (on-chain):** 0xcfd1445fe32e3cd61570441481b6861a6508f4873ceb476920c1d26d034eb8a2
**Severity:** high

**Description:**
**Description**\
The `execTransactionOnBehalf` function in the `PalmeraModule` contract allows certain roles (Safe Lead, Super Safe, Root Safe) to execute transactions on behalf. However, there is a potential vulnerability that can be exploited if the `to` address is malicious. Specifically, if the operation is set to Enum.Operation.DelegateCall, a malicious contract at the to address can execute a selfdestruct operation, leading to the destruction of the targetSafe contract. This can severely disrupt the organization by breaking contract modules and halting all transactions.
`this occur when the one of the caller who is being removed from their position use this exploit and destory the contracts/org.`


**Attack Scenario**\
1. execTransactionOnBehalf function calls

```
    result = safeTarget.execTransactionFromModule(to, value, data, operation);
```
2. Internal Execution:
The execTransactionFromModule function internally calls the execute function:
```
    function execute(
        address to,
        uint256 value,
        bytes memory data,
        Enum.Operation operation,
        uint256 txGas
    ) internal returns (bool success) {
        if (operation == Enum.Operation.DelegateCall) {
            assembly {
                success := delegatecall(txGas, to, add(data, 0x20), mload(data), 0, 0)
            }
        } else {
            assembly {
                success := call(txGas, to, value, add(data, 0x20), mload(data), 0, 0)
            }
        }
    }
```
3. Delegate Call Vulnerability:
operation is Enum.Operation.DelegateCall, the delegatecall opcode is used.
delegatecall executes code from the to address in the context of the calling contract (targetSafe).
If the to address is a malicious contract containing a selfdestruct operation, it can destroy the targetSafe contract.

4. Potential Exploit Scenario:
An authorized caller (e.g., Safe Lead, Super Safe, Root Safe) with malicious intent or a compromised account can call execTransactionOnBehalf with a malicious to address.
This can occur when one of the owners or a caller who is being removed from their position front-runs the transaction and destroys the targetSafe contract.
The malicious contract at the to address executes a selfdestruct operation via delegatecall.
This results in the destruction of the targetSafe contract, breaking the organization’s contract modules and halting all transactions.

Example Exploit Code
A malicious contract could look like this:
```
contract MaliciousContract {
    function destroy(address target) external {
        selfdestruct(payable(target));
    }
}
```
**Attachments**

1. **Proof of Concept (PoC) File**
<!-- You must provide a file containing a proof of concept (PoC) that demonstrates the vulnerability you have discovered. -->
```
function execTransactionOnBehalf(
        bytes32 org,
        address superSafe, // can be root or super safe
        address targetSafe,
        address to,
        uint256 value,
        bytes calldata data,
        Enum.Operation operation,
        bytes memory signatures
    )
        external
        payable
        nonReentrant
        SafeRegistered(superSafe)
        SafeRegistered(targetSafe)
        Denied(org, to)
        returns (bool result)
    {
        address caller = _msgSender();
        // Caller is Safe Lead: bypass check of signatures
        // Caller is another kind of wallet: check if it has the corrects signatures of the root/super safe
        if (!isSafeLead(getSafeIdBySafe(org, targetSafe), caller)) {
            // Check if caller is a superSafe of the target safe (checking with isTreeMember because is the same method!!)
            if (hasNotPermissionOverTarget(superSafe, org, targetSafe)) {
                revert Errors.NotAuthorizedExecOnBehalf();
            }
            // Caller is a safe then check caller's safe signatures.
            bytes memory palmeraTxHashData = encodeTransactionData(
                /// Palmera Info
                org,
                superSafe,
                targetSafe,
                /// Transaction info
                to,
                value,
                data,
                operation,
                /// Signature info
                nonce[org]
            );
            /// Verify Collision of Nonce with multiple txs in the same range of time, study to use a nonce per org

            ISafe leadSafe = ISafe(superSafe);
            bytes memory sortedSignatures = processAndSortSignatures(
                keccak256(palmeraTxHashData), signatures, leadSafe.getOwners()
            );
            leadSafe.checkSignatures(
                keccak256(palmeraTxHashData),
                palmeraTxHashData,
                sortedSignatures
            );
        }
        /// Increase nonce and execute transaction.
        nonce[org]++;
        /// Execute transaction from target safe
        ISafe safeTarget = ISafe(targetSafe);
        result =
            safeTarget.execTransactionFromModule(to, value, data, operation);

        if (!result) revert Errors.TxOnBehalfExecutedFailed();
        emit Events.TxOnBehalfExecuted(
            org, caller, superSafe, targetSafe, result
        );
    }
```

2. **Revised Code File (Optional)**
<!-- If possible, please provide a second file containing the revised code that offers a potential fix for the vulnerability. This file should include the following information:
- Comment with a clear explanation of the proposed fix.
- The revised code with your suggested changes.
- Any additional comments or explanations that clarify how the fix addresses the vulnerability. -->
To mitigate this vulnerability, additional checks should be implemented to ensure the to address is not malicious. Specifically, avoid using delegatecall with untrusted addresses
