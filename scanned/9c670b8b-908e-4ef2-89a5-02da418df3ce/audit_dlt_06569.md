# [M] Enum is not present in EIP-712

## Summary
Severity: Medium
Chain: Smart contract
Component: Palmera
Published: 2024-06-24
Source: https://github.com/hats-finance/Palmera-0x5fee7541ddcd51ba9f4af606f87b2c42eea655be/issues/11
Type: hats-finding

## Details
**Github username:** @SB-Security
**Twitter username:** SBSecurity_
**Submission hash (on-chain):** 0xded09c8daa3665d393f5976c8f7e0bb2bf0720c579734fa1bb0f153a775f6a50
**Severity:** medium

**Description:**
**Description**\
Enum.Operation is not common type and cannot be used in EIP-712 hash.

**Attack Scenario**\
Enums are derived from uint and uint should be used instead, using 
Enum.Operation will make the hash wrong.
**Attachments**

1. **Proof of Concept (PoC) File**
```
function createDigestExecTx(
        bytes32 domainSeparatorSafe,
        Transaction memory safeTx
    ) public view returns (bytes32) {
        bytes32 digest = _hashTypedDataV4(
            domainSeparatorSafe,
            keccak256(
                abi.encode(
                    keccak256(
                        "execTransaction(address to,uint256 value,bytes data,Enum.Operation operation,uint256 safeTxGas,uint256 baseGas,uint256 gasPrice,address gasToken,address refundReceiver,bytes signatures)"
                    ),
                    safeTx.to,
                    safeTx.value,
                    safeTx.data,
                    safeTx.operation,
                    safeTx.safeTxGas,
                    safeTx.baseGas,
                    safeTx.gasPrice,
                    safeTx.gasToken,
                    safeTx.refundReceiver,
                    safeTx.signatures
                )
```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Palmera-0x5fee7541ddcd51ba9f4af606f87b2c42eea655be/issues/11_
