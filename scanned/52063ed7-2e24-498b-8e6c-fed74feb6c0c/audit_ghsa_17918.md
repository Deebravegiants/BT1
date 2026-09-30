# [H] Adminer PHP Object Injection issue leads to Denial of Service

## Summary
Severity: High
Advisory: GHSA-mqh4-2mm8-g7w9
CVE: CVE-2025-43960
CWE: CWE-502
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:L (CVSS_V3)
Published: 2025-08-25
Source: https://github.com/advisories/GHSA-mqh4-2mm8-g7w9
Type: github-advisory

## Affected
- Packagist: `vrana/adminer` — affected >=0

## Details
Adminer 4.8.1, when using Monolog for logging, allows a Denial of Service (memory consumption) via a crafted serialized payload (e.g., using s:1000000000), leading to a PHP Object Injection issue. Remote, unauthenticated attackers can trigger this by sending a malicious serialized object, which forces excessive memory usage, rendering Adminer’s interface unresponsive and causing a server-level DoS. While the server may recover after several minutes, multiple simultaneous requests can cause a complete crash requiring manual intervention.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-43960
- https://github.com/far00t01/CVE-2025-43960
- https://github.com/vrana/adminer
