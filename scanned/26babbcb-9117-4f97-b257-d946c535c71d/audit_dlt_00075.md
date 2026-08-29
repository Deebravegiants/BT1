# [C] rk Identity Point Panic in Transaction Verification

## Summary
Severity: Critical
Chain: Zcash
Component: ZcashFoundation/zebra
CVE: CVE-2026-41584
Published: 2026-04-17
Source: https://github.com/ZcashFoundation/zebra/security/advisories/GHSA-452v-w3gx-72wg
Type: github-advisory

## Details
# CVE-2026-XXXXX: rk Identity Point Panic in Transaction Verification

## Summary

Orchard transactions contain a `rk` field which is a randomized validating key and also an elliptic curve point. The Zcash specification allows the field to be the identity (a "zero" value), however, the `orchard` crate which is used to verify Orchard proofs would panic when fed a `rk` with the identity value. Thus an attacker could send a crafted transaction that would make a Zebra node crash.

## Severity

**Critical** - This is a Denial of Service Vulnerability that could allow an attacker to crash Zebra nodes.

## Affected Versions

All Zebra versions prior to **version 4.3.1**.

## Description

The vulnerability exists in the `circuits.rs` file of the `orchard` crate; it attempts to get the coordinates of the `rk` value and calls `unwrap()` on the results, which causes a panic if `rk` is the identity.

Zebra parses `rk` as a byte vector; it creates an Orchard "bundle" using the `orchard` crate and then calls the same crate to verify it, triggering the panic.

An attacker could exploit this by:
1. Creating a transaction with a identity `rk`
2. Submitting it to a Zebra node, making it crash

## Impact

**Denial of Service**

* **Attack Vector:** Network.
* **Effect:** Node crash.
* **Scope:** Any impacted Zebra node.

## Fixed Versions

This issue is fixed in **Zebra 4.3.1**. 

The fix was agreed with `zcashd` developers (which has the same issue) to not allow the identity `rk` anymore and change the specification as such. Zebra now does this when parsing a transaction. This was deemed easier than fixing the issue in `orchard`, which would make the bug public before the nodes could be patched.


_Trimmed to 38 lines — full report: https://github.com/ZcashFoundation/zebra/security/advisories/GHSA-452v-w3gx-72wg_
