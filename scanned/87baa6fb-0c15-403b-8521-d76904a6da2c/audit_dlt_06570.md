# [H] Unbonded `orgHash` Could Result in Denial of Service (DOS)

## Summary
Severity: High
Chain: Smart contract
Component: Palmera
Published: 2024-06-24
Source: https://github.com/hats-finance/Palmera-0x5fee7541ddcd51ba9f4af606f87b2c42eea655be/issues/10
Type: hats-finding

## Details
**Github username:** @0xmahdirostami
**Twitter username:** 0xmahdirostami
**Submission hash (on-chain):** 0x03beff97c48e17388e7e20e197e82bf6aef4a2695474d532517022731f6536a9
**Severity:** high

**Description:**
**Description**:
Unbonded `orgHash` could result in a denial of service (DOS) in several functions, potentially leading to serious issues. The affected functions are:
- `getOrgBySafe`
- `removeOrg`
- `getOrgHashBySafe`


**Impact**:
Denial of service in core functions, potentially affecting the integrity and usability of the contract.
A DOS attack in the `removeOrg` function can also cause issues when attempting to remove an organization from the list of organization hashes. (due to this I set it as high)


**Scenario**:
An attacker can exploit unbonded `orgHash` to cause these functions to fail, preventing legitimate users from interacting with the contract. For example:
1. An attacker creates lots of orgs..
2. The contract becomes unable to process legitimate `orgHash` values due to the presence of unbonded values, leading to DOS in the mentioned functions.
