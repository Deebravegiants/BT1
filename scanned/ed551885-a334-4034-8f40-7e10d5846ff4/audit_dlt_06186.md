# [H] Domain separators are susceptible to replay attacks, ticket rewards can be claimed twice

## Summary
Severity: High
Chain: Smart contract
Component: SafeStaking-by-HOPR
Published: 2023-10-06
Source: https://github.com/hats-finance/SafeStaking-by-HOPR-0x607386df18b663cf5ee9b879fbc1f32466ad5a85/issues/17
Type: hats-finding

## Details
**Github username:** @0xfuje
**Submission hash (on-chain):** 0xf9626ce34861c300afafbce036ca9d3a9b1860c8c651f8fbacec316607545b1a
**Severity:** high

**Description:**
## Impact
Winning tickets can be redeemed for rewards twice,  functions can use incorrect domain separator

## Description
In case of a hard fork a malicious node operator can claim his ticket rewards twice via `Channels.sol` - `redeemTicket()`. The root of the problem is that `updateDomainSeparator()` does not entirely prevent replay attacks when a hard fork happens because:
1. it's a public function, BUT none of the functions that use `domainSeparator` verify `block.chainid` it is up to date
2. it can be front-runned by the attacker on both chains to cause a replay attack
3. the attacker can simply redeem on both chains before anyone calls `updateDomainSeparator()` since none of the functions call it

`Channels.sol` - [`updateDomainSeparator()`](https://github.com/hats-finance/SafeStaking-by-HOPR-0x607386df18b663cf5ee9b879fbc1f32466ad5a85/blob/master/packages/ethereum/contracts/src/Channels.sol#L284-L300)
```solidity
    function updateDomainSeparator() public {
        // following encoding guidelines of EIP712
        bytes32 newDomainSeparator = keccak256(
            abi.encode(
                keccak256("EIP712Domain(string name,string version,uint256 chainId,address verifyingContract)"),
                keccak256(bytes("HoprChannels")),
                keccak256(bytes(VERSION)),
                block.chainid,
                address(this)
            )
        );

        if (newDomainSeparator != domainSeparator) {
            domainSeparator = newDomainSeparator;
            emit DomainSeparatorUpdated(domainSeparator);
        }
    }
```

A smart attacker can plan ahead on the news of a planned hard-fork and accumulate as much redeemable tickets as possible and setup a front-running bot to double claim his rewards before `updateDomainSeparator()` is called.

---

_Trimmed to 38 lines — full report: https://github.com/hats-finance/SafeStaking-by-HOPR-0x607386df18b663cf5ee9b879fbc1f32466ad5a85/issues/17_
