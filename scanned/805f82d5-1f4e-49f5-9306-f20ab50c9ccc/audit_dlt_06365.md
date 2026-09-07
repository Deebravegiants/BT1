# [M] EIP712 chainId is hardcoded which can cause replay attacks in case of hardfork

## Summary
Severity: Medium
Chain: Smart contract
Component: Paladin
Published: 2024-02-07
Source: https://github.com/hats-finance/Paladin-0x1610bfde27e57b068af7f38aec3d2a7b1d146989/issues/16
Type: hats-finding

## Details
**Github username:** @0xRizwan
**Twitter username:** 0xRizwann
**Submission hash (on-chain):** 0xd544a38eee3a234f491edaff405600deec3135b397cb18630fdc901889fcdc0b
**Severity:** medium

**Description:**
**Description**\

`BoostV2.vy` is the boost delegation contract with Version V2 and written in Vyper language. This contract has implemented EIP 712-signed approvals through a [permit()](https://github.com/hats-finance/Paladin-0x1610bfde27e57b068af7f38aec3d2a7b1d146989/blob/cf3c82f102a76f58acf003980c480eb9028f0e94/contracts/boost/BoostV2.vy#L362) function. A domain separator and the chainID are included in the signature schema. However, this chainID is fixed at the time of
contract initialization.

```solidity
@external
def __init__(_ve: address):
    DOMAIN_SEPARATOR = keccak256(_abi_encode(EIP712_TYPEHASH, keccak256(NAME), keccak256(VERSION), chain.id, self))
    HOLY_PAL_POWER = _ve

    log Transfer(ZERO_ADDRESS, msg.sender, 0)
```

Per EIP712, calculating the domain separator using a hardcoded chainId could pose problems. The reason is that if the chain undergoes a hard fork and changes its chain id, the domain separator will be inaccurately calculated. In addition, per current implementation DOMAIN_SEPARATOR is immutable which it should not be.

```solidity
DOMAIN_SEPARATOR: immutable(bytes32)
```

**Impact**

After the chain hardfork then `DOMAIN_SEPARATOR` value will become invalid. This is because the chainId parameter is computed in `__init__` initialization. This means even after hard fork chainId would remain same which is incorrect and could cause possible replay attacks.  The chainId is hardcoded in `DOMAIN_SEPARATOR` which means even after hard fork, DOMAIN_SEPARATOR value will remain same and point to incorrect chainId.

**Recommendation**\

It is recommended to adhere to the best practices of the EIP712 implementation. To avoid this issue, the domain separator should be dynamically calculated using the chainId opcode each time it is requested.

I highly recommend to check openzeppelin's EIP712.sol for correct implementation [here](https://github.com/OpenZeppelin/openzeppelin-contracts/blob/17a8955cd8ed2c9a269421a11c2e2774b796e305/contracts/utils/cryptography/EIP712.sol#L80-L90)


**References**

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Paladin-0x1610bfde27e57b068af7f38aec3d2a7b1d146989/issues/16_
