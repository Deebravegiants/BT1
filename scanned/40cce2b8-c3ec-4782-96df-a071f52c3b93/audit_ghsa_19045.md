# [H] node-forge has ASN.1 Unbounded Recursion

## Summary
Severity: High
Advisory: GHSA-554w-wpv2-vw27
CVE: CVE-2025-66031
CWE: CWE-674
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-11-26
Source: https://github.com/advisories/GHSA-554w-wpv2-vw27
Type: github-advisory

## Affected
- npm: `node-forge` — affected >=0 <1.3.2

## Details
### Summary

An Uncontrolled Recursion (CWE-674) vulnerability in node-forge versions 1.3.1 and below enables remote, unauthenticated attackers to craft deep ASN.1 structures that trigger unbounded recursive parsing. This leads to a Denial-of-Service (DoS) via stack exhaustion when parsing untrusted DER inputs.

### Details

An ASN.1 Denial of Service (Dos) vulnerability exists in the node-forge `asn1.fromDer` function within `forge/lib/asn1.js`. The ASN.1 DER parser implementation (`_fromDer`) recurses for every constructed ASN.1 value (SEQUENCE, SET, etc.) and lacks a guard limiting recursion depth. An attacker can craft a small DER blob containing a very large nesting depth of constructed TLVs which causes the Node.js V8 engine to exhaust its call stack and throw `RangeError: Maximum call stack size exceeded`, crashing or incapacitating the process handling the parse. This is a remote, low-cost Denial-of-Service against applications that parse untrusted ASN.1 objects.

### Impact

This vulnerability enables an unauthenticated attacker to reliably crash a server or client using node-forge for TLS connections or certificate parsing.

This vulnerability impacts the ans1.fromDer function in `node-forge` before patched version `1.3.2`. 

Any downstream application using this component is impacted. These components may be leveraged by downstream applications in ways that enable full compromise of availability.

## References
- https://github.com/digitalbazaar/forge/security/advisories/GHSA-554w-wpv2-vw27
- https://github.com/digitalbazaar/forge/commit/260425c6167a38aae038697132483b5517b26451
- https://github.com/digitalbazaar/forge
