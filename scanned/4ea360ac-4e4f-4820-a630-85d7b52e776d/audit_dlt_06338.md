# [M] `TYPEHASH` passed in `Bfx.withdraw()` does not comply EIP-712 and will return incorrect `digest`

## Summary
Severity: Medium
Chain: Smart contract
Component: Blast-Futures-Exchange
Published: 2024-02-06
Source: https://github.com/hats-finance/Blast-Futures-Exchange-0x97895c329b950755566ddcdad3395caaea395074/issues/37
Type: hats-finding

## Details
**Github username:** --
**Twitter username:** --
**Submission hash (on-chain):** 0x8b05ad57d1bfe0a4011489339bc489f3e09bf0ede069ea92cf2585fc7c3f7ae4
**Severity:** medium

**Description:**
**Description**\

`Bfx.withdraw()` allows a withdrawal operation with EIP-712 signature verification.


```solidity

    function withdraw(
        uint256 id, address trader, uint256 amount, uint8 v, bytes32 r, bytes32 s
        ) external nonReentrant {

   . . .some code

        bytes32 digest = _hashTypedDataV4(keccak256(abi.encode(
            keccak256("withdrawal(uint256 id,address trader,uint256 amount)"),
            id,
            trader,
            amount
        )));

   . . .some code

    }
```

For digest, _hashTypedDataV4() is taken from openzeppelin EIP712.sol which is compliant to EIP-712. This function takes `TYPEHASH` as one of the argument to retrun the bytes32 `digest`.

Here in `Bfx.withdraw()`, `TYPEHASH = keccak256("withdrawal(uint256 id,address trader,uint256 amount)"`

Since, the protocol documentation ensures the withdrawal comply 100% with EIP712, However, the above `TYPEHASH` does not comply with EIP712.

EIP712 is used for `Typed structured data hashing and signing`. and data used in `TYPEHASH` is the structured data.

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Blast-Futures-Exchange-0x97895c329b950755566ddcdad3395caaea395074/issues/37_
