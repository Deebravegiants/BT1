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

For example, Per EIP712, 

```solidity

struct Mail {
    address from;
    address to;
    string contents;
}

bytes32 constant MAIL_TYPEHASH = keccak256(
  "Mail(address from,address to,string contents)");
```

It can be seen, a struct named `Mail` is used with keccak256 to hash to get the `MAIL_TYPEHASH`.

Now, if you see the current implementation, `keccak256("withdrawal(uint256 id,address trader,uint256 amount)"`

then `withdrawal` is struct name which does not match the struct defination. The first letter of struct should be capital, like `Withdrawal` and NOT `withdrawal`

Since, [solidity](https://docs.soliditylang.org/en/latest/style-guide.html#struct-names)  specifically mentions,

> Structs should be named using the CapWords style. Examples: MyCoin


This is due to a single letter will give entirely different hash by keccak256. If you see, here the difference is only about small letter `m` and capital letter `M`.

While testing the `TYPEHASH` in `Remix IDE`, the results are different.

With current implementation given in contract i.e 

```solidity
bytes32 public constant WITHDRAWAL_TYPEHASH = keccak256("withdrawal(uint256 id,address trader,uint256 amount)");
```

The result is `0xec976281d6462ad970e7a9251148e624b8aa376c6857d4245700b1b711bb0884`

and the proposed recommendation i.e incompliance with EIP712

```solidity
bytes32 public WITHDRAWAL_TYPEHASH = keccak256("Withdrawal(uint256 id,address trader,uint256 amount)");
```

The result is `0x92351042d160b58aef05f219c6acec14f0d71e7be3befc892862667ae62b1a96`


It can be seen that keccak256 produces different hash in both scenarios.

However, the current implementation deviates from EIP712 and solidity struct naming defination. This will return incorrect digest and hamper overall working of EIP712 withdrawal process for which the Blast-Future Exchange wants to comply with. Below recommendation mitigate the issue.

**Recommendation**\

Recommend to modifiy the code as below so that TYPEHASH should be as per EIP712.


```diff


+  bytes32 public WITHDRAWAL_TYPEHASH = keccak256("Withdrawal(uint256 id,address trader,uint256 amount)");   @audit //Now, Withdrawal struct defination is per EIP712 and solidity naming convention.


    function withdraw(
        uint256 id, address trader, uint256 amount, uint8 v, bytes32 r, bytes32 s
        ) external nonReentrant {

   . . .some code

-        bytes32 digest = _hashTypedDataV4(keccak256(abi.encode(
-            keccak256("withdrawal(uint256 id,address trader,uint256 amount)"),
-            id,
-            trader,
-            amount
-        )));


+        bytes32 digest = _hashTypedDataV4(keccak256(abi.encode(
+            WITHDRAWAL_TYPEHASH,
+            id,
+            trader,
+            amount
+        )));

   . . .some code

    }
```
