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

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Palmera-0x5fee7541ddcd51ba9f4af606f87b2c42eea655be/issues/61_
