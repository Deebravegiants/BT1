# [M] node-forge is vulnerable to ASN.1 OID Integer Truncation

## Summary
Severity: Medium
Advisory: GHSA-65ch-62r8-g69g
CVE: CVE-2025-66030
CWE: CWE-190
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-11-26
Source: https://github.com/advisories/GHSA-65ch-62r8-g69g
Type: github-advisory

## Affected
- npm: `node-forge` — affected >=0 <1.3.2

## Details
### Summary

**MITRE-Formatted CVE Description**
An Integer Overflow (CWE-190) vulnerability in node-forge versions 1.3.1 and below enables remote, unauthenticated attackers to craft ASN.1 structures containing OIDs with oversized arcs. These arcs may be decoded as smaller, trusted OIDs due to 32-bit bitwise truncation, enabling the bypass of downstream OID-based security decisions.

### Description

An ASN.1 OID Integer Truncation vulnerability exists in the node-forge `asn1.derToOid` function within `forge/lib/asn1.js`. OID components are decoded using JavaScript's bitwise left-shift operator (`<<`), which forcibly casts values to 32-bit signed integers. Consequently, if an attacker provides a mathematically unique, very large OID arc integer exceeding $2^{31}-1$, the value silently overflows and wraps around rather than throwing an error. 

### Impact

This vulnerability allows a specially crafted ASN.1 object to spoof an OID, where a malicious certificate with a massive, invalid OID is misinterpreted by the library as a trusted, standard OID, potentially bypassing security controls.

This vulnerability impacts the `asn1.derToOid` function in `node-forge` before patched version `1.3.2`. 

Any downstream application using this component is impacted. This component may be leveraged by downstream applications in ways that enables partial compromise of integrity, leading to potential availability and confidentiality compromises.

## References
- https://github.com/digitalbazaar/forge/security/advisories/GHSA-65ch-62r8-g69g
- https://nvd.nist.gov/vuln/detail/CVE-2025-66030
- https://github.com/digitalbazaar/forge/commit/3e0c35ace169cfca529a3e547a7848dc7bf57fdb
- https://github.com/digitalbazaar/forge
