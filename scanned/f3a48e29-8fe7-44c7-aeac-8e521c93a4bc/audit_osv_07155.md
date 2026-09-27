# [M] BIT-node-2024-22025

## Summary
Severity: Medium
Advisory: BIT-node-2024-22025
Aliases: BIT-node-min-2024-22025, CVE-2024-22025
Ecosystem: Bitnami
Published: 2024-06-04
Source: https://osv.dev/vulnerability/BIT-node-2024-22025
Type: osv

## Affected
- Bitnami: `node` — affected >=21.0.0 <21.6.2

## Details
A vulnerability in Node.js has been identified, allowing for a Denial of Service (DoS) attack through resource exhaustion when using the fetch() function to retrieve content from an untrusted URL.
The vulnerability stems from the fact that the fetch() function in Node.js always decodes Brotli, making it possible for an attacker to cause resource exhaustion when fetching content from an untrusted URL.
An attacker controlling the URL passed into fetch() can exploit this vulnerability to exhaust memory, potentially leading to process termination, depending on the system configuration.

## References
- https://hackerone.com/reports/2284065
- https://lists.debian.org/debian-lts-announce/2024/03/msg00029.html
- https://security.netapp.com/advisory/ntap-20240517-0008/
- https://nvd.nist.gov/vuln/detail/CVE-2024-22025
- https://lists.debian.org/debian-lts-announce/2024/09/msg00029.html
- https://github.com/nodejs/node/releases/tag/v18.19.1
- https://github.com/nodejs/node/releases/tag/v20.11.1
- https://github.com/nodejs/node/releases/tag/v21.6.2
