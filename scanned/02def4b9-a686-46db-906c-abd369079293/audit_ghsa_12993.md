# [C] PyroCMS remote code execution vulnerability

## Summary
Severity: Critical
Advisory: GHSA-w7vm-4v3j-vgpw
CVE: CVE-2023-29689
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-08-04
Source: https://github.com/advisories/GHSA-w7vm-4v3j-vgpw
Type: github-advisory

## Affected
- Packagist: `pyrocms/pyrocms` — affected >=0

## Details
PyroCMS 3.9 contains a remote code execution (RCE) vulnerability that can be exploited through a server-side template injection (SSTI) flaw. This vulnerability allows a malicious attacker to send customized commands to the server and execute arbitrary code on the affected system.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-29689
- https://cupc4k3.lol/ssti-leads-to-rce-on-pyrocms-7515be27c811
- https://github.com/pyrocms/pyrocms
- http://packetstormsecurity.com/files/174088/Pyro-CMS-3.9-Server-Side-Template-Injection.html
