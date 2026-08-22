# [M] addr/addrv2 Deserialization Resource Exhaustion

## Summary
Severity: Medium
Chain: Zcash
Component: ZcashFoundation/zebra
CVE: CVE-2026-40881
CWE: Allocation of Resources Without Limits or Throttling
Published: 2026-04-17
Source: https://github.com/ZcashFoundation/zebra/security/advisories/GHSA-xr93-pcq3-pxf8
Type: github-advisory

## Details
# CVE-2026-40881: addr/addrv2 Deserialization Resource Exhaustion

## Summary

When deserializing `addr` or `addrv2` messages, which contain vectors of addresses, Zebra would fully deserialize them up to a maximum length (over 233,000) that was derived from the 2 MiB message size limit. This is much larger than the actual limit of 1,000 messages from the specification. Zebra would eventually check that limit but, at that point, the memory for the larger vector was already allocated. An attacker could cause out-of-memory aborts in Zebra by sending multiple such messages over different connections.

## Severity

**Moderate** - This is a Denial of Service Vulnerability that could allow an attacker to crash a Zebra node.

## Affected Versions

All Zebra versions prior to **version 4.3.1**.

## Description

The vulnerability exists in the `read_addr/addrv2` functions in `codec.rs`. It deserializes a vector of addresses with the `zcash_deserialize()` trait method, which uses as a upper bound the result of `T::max_allocation()`. For theses types, it was derived from dividing the max message size (2 MiB) by the minimum serialized size of one entry. For AddrV1: 2_097_152 / 30 = 69,904. For AddrV2: 2_097_152 / 9 = 233,016. Only after deserialization was the `MAX_ADDRS_IN_MESSAGE = 1000` limit checked.

An attacker could exploit this by:
1. Creating `addr` or `addrv2` messages with a large number of entries.
2. Submitting them to a Zebra node, possibly through multiple connections, to attempt to get Zebra into an out-of-memory state.

## Impact

**Denial of Service**

* **Attack Vector:** Network.
* **Effect:** Zebra node crash.
* **Scope:** Any impacted Zebra node.

## Fixed Versions

This issue is fixed in **Zebra 4.3.1**. 

The fix changes the `max_allocation()` method for the relevant types to return 1,000, thus blocking larger values prior to deserialization.

## Mitigation


_Trimmed to 38 lines — full report: https://github.com/ZcashFoundation/zebra/security/advisories/GHSA-xr93-pcq3-pxf8_
