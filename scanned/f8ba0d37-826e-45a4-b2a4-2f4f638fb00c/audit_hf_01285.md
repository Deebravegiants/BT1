# [M] ERC20: Memory unsafe assembly is not future proof

## Summary
Severity: Medium
Contest weight: 0.5929
Dataset id: 6053
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
The DOMAIN_SEPARATOR() method in the ERC20 mixin has 2 direct inline-assembly blocks both
of which are marked "memory safe" despite violating memory safety guarantees. Speciﬁcally, it stores a
reference to and writes to memory which may not be free.
1. The method locally caches the free memory pointer in result:
/// @solidity memory-safe-assembly
assembly {
    result := mload(0x40) // Grab the free memory pointer.
}
2. Calls name(), a memory-using, view method
403:
bytes32 nameHash = keccak256(bytes(name()));
3. Uses the previously cached free memory pointer to directly write to memory:
/// @solidity memory-safe-assembly
assembly {
    let m := result
    // `keccak256("EIP712Domain(string name,string version,uint256 chainId,address verifyingContract)")`.
    // forgefmt: disable-next-item
    mstore(m, 0x8b73c3c69bb8fe3d512ecc4cf759cc79239f7b179b0ffacaa9a75d522b39400f)
    mstore(add(m, 0x20), nameHash)
    // `keccak256("1")`.
    // forgefmt: disable-next-item
    mstore(add(m, 0x40), 0xc89efdaa54c0f20c7adf612882df0950f5a951637e0307cdcb4c672f298b8bc6)
    mstore(add(m, 0x60), chainid())
    mstore(add(m, 0x80), address())
    result := keccak256(m, 0xa0)
}
```
This may not be memory-safe because name() may also read and use the free memory pointer which is
then overwritten. Standalone this seems to work as the result string of name() does not need to persist,
being immediately consumed by the keccak256 function.
Nevertheless, future improvements to Solidity's optimizer may allow for reasonable uses of this library to
result in incorrect code.
Potential Scenario:
A developer uses the Solady library, writing a function where name() (overridden as a pure function) and
DOMAIN_SEPARATOR() are both used within a new method:
```solidity
function getMetadata() public view returns (bytes32, string memory) {
    return (DOMAIN_SEPARATOR(), name());
}
```
A more sophisticated Solidity compiler + optimizer compiles the code, considering its structure:
• The name() method is pure, meaning it has no side effects or mutable dependencies outside of its
(0) paramters
• The DOMAIN_SEPARATOR() method relies on the value of name()
• All assembly blocks within DOMAIN_SEPARATOR() are marked "memory safe"
based on the facts above the optimizer decides to inline DOMAIN_SEPARATOR() into the getMetadata() func-
tion (hypothetical inlined version):
```solidity
function inlined__getMetadata() public view returns (bytes32, string memory) {
    bytes32 result__DOMAIN_SEPARATOR;
    /// @solidity memory-safe-assembly
    assembly {
        result__DOMAIN_SEPARATOR := mload(0x40) // Grab the free memory pointer.
    }
    //
    We simply calculate it on-the-fly to allow for cases where the `name` may change.
    string memory name__inlined = name();
    bytes32 nameHash = keccak256(bytes(name__inlined));
    /// @solidity memory-safe-assembly
    assembly {
        let m := result__DOMAIN_SEPARATOR
        // `keccak256("EIP712Domain(string name,string version,uint256 chainId,address verifyingContract)")`.
        // forgefmt: disable-next-item
        mstore(m, 0x8b73c3c69bb8fe3d512ecc4cf759cc79239f7b179b0ffacaa9a75d522b39400f)
        mstore(add(m, 0x20), nameHash)
        // `keccak256("1")`.
        // forgefmt: disable-next-item
        mstore(add(m, 0x40), 0xc89efdaa54c0f20c7adf612882df0950f5a951637e0307cdcb4c672f298b8bc6)
        mstore(add(m, 0x60), chainid())
        mstore(add(m, 0x80), address())
        result__DOMAIN_SEPARATOR := keccak256(m, 0xa0)
    }
    return (result__DOMAIN_SEPARATOR, name__inlined);
}
```
This would then produce incorrect results because the memory unsafe code from DOMAIN_SEPARATOR()
would cause the data within name() to be overwritten.

## Recommendation
In DOMAIN_SEPARATOR() retrieve the free memory pointer after calling name().
