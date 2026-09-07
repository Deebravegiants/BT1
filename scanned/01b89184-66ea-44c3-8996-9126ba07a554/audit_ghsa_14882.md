# [C] qdrant is vulnerable to path traversal due to improper input validation in the `/collections/{name}/snapshots/upload` endpoint

## Summary
Severity: Critical
Advisory: GHSA-xcr2-h8hv-6227
CVE: CVE-2024-3584
CWE: CWE-20
Ecosystem: crates.io
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-06-02
Source: https://github.com/advisories/GHSA-xcr2-h8hv-6227
Type: github-advisory

## Affected
- crates.io: `qdrant` — affected >=1.9.0-dev <1.9.0

## Details
qdrant/qdrant version 1.9.0-dev is vulnerable to path traversal due to improper input validation in the `/collections/{name}/snapshots/upload` endpoint. By manipulating the `name` parameter through URL encoding, an attacker can upload a file to an arbitrary location on the system, such as `/root/poc.txt`. This vulnerability allows for the writing and overwriting of arbitrary files on the server, potentially leading to a full takeover of the system. The issue is fixed in version 1.9.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-3584
- https://github.com/qdrant/qdrant/commit/15479a45ffa3b955485ae516696f7e933a8cce8a
- https://github.com/qdrant/qdrant
- https://huntr.com/bounties/5c7c82e2-4873-40b7-a5f3-0f4a42642f73
