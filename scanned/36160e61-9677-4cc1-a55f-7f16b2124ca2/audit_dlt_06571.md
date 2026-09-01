# [M] Incorrect encoding of bytes for EIP712 `digest ` in createDigestExecTx()  functions thus not compatible with EIP712

## Summary
Severity: Medium
Chain: Smart contract
Component: Palmera
Published: 2024-06-24
Source: https://github.com/hats-finance/Palmera-0x5fee7541ddcd51ba9f4af606f87b2c42eea655be/issues/6
Type: hats-finding

## Details
**Github username:** --
**Twitter username:** --
**Submission hash (on-chain):** 0x3d8e0be59cc1e1447972ce1ffa03b3545e35280084af68c072989160a8637746
**Severity:** medium

**Description:**
**Description**\

```solidity

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
@>                    safeTx.data,
                    safeTx.operation,
                    safeTx.safeTxGas,
                    safeTx.baseGas,
                    safeTx.gasPrice,
                    safeTx.gasToken,
                    safeTx.refundReceiver,
@>                    safeTx.signatures
                )
            )
        );

        return digest;
    }
```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Palmera-0x5fee7541ddcd51ba9f4af606f87b2c42eea655be/issues/6_
