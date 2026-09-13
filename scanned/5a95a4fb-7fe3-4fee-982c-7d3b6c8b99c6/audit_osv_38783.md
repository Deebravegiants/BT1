# [M] XRDP is vulnerable to a server timing attack, leading to user enumeration

## Summary
Severity: Medium
Advisory: CVE-2026-42218
Aliases: GHSA-3wr5-fwmh-qh34
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-07-20
Source: https://osv.dev/vulnerability/CVE-2026-42218
Type: osv

## Details
xrdp is an open source RDP server. Versions 0.10.6 and prior contain a timing side-channel vulnerability in the login interface. Due to a discrepancy in response processing times, a remote attacker can infer the existence of a username on the system, leading to unauthorized information disclosure via username enumeration. This issue has been fixed in version 0.10.6.1.

## References
- https://github.com/neutrinolabs/xrdp/releases/tag/v0.10.6.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/42xxx/CVE-2026-42218.json
- https://github.com/neutrinolabs/xrdp/security/advisories/GHSA-3wr5-fwmh-qh34
- https://nvd.nist.gov/vuln/detail/CVE-2026-42218
