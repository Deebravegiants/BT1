# [M] Remove `nonce` argument from `permit` functions

## Summary
Severity: Medium
Source: https://github.com/ethereum/EIPs/blob/8a34d644aacf0f9f8f00815307fd7dd5da07655f/EIPS/eip-2612.md
Type: audit-issue

## Details
#### Description

The [EIP-2612](https://github.com/ethereum/EIPs/blob/8a34d644aacf0f9f8f00815307fd7dd5da07655f/EIPS/eip-2612.md) specifies a way for a token owner to `approve` tokens for a spender without any gas costs for themselves. This is also a good way to allow a 3rd party to enable `approve` before a `transferFrom`, in the same transaction.

The standard specifies a new `permit` function that looks like this:

```solidity
function permit(
    address owner, 
    address spender, 
    uint256 value, 
    uint256 deadline, 
    uint8 v, 
    bytes32 r, 
    bytes32 s
)
```

The function in the standard does not have a `nonce` argument and as [clarified by the standard creator](https://github.com/ethereum/EIPs/pull/2612/files#r451351487), the nonce does not need to be specified, as it can be used from the contract storage.

However, the current `permit` implementation does contain that `nonce`


**code/contracts/token/AaveToken.sol:L92-L101**
```solidity
function permit(
    address owner,
    address spender,
    uint256 nonce,
    uint256 expiration,
    uint256 amount,
    uint8 v,
    bytes32 r,
    bytes32 s
) external {
```

In order to match the EIP-2612 standard, the `permit` function needs to be changed in the following manner:

- remove the `nonce` argument in the function definition
- remove the `require` which checks if the provided **nonce** matches the **nonce** in the contract storage
- to generate the digest, use the **nonce** currently available in the contract storage
- if the signature is valid, increment the **nonce** in the contract storage.

#### Recommendation

Remove the `nonce` argument and make the necessary changes in the code and the matching tests to match the EIP-2612 spec.
