# [M] Task Hijacking in hamza417/inure

## Summary
Severity: Medium
Advisory: CVE-2024-0245
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2025-03-20
Source: https://osv.dev/vulnerability/CVE-2024-0245
Type: osv

## Details
A misconfiguration in the AndroidManifest.xml file in hamza417/inure before build97 allows for task hijacking. This vulnerability permits malicious applications to inherit permissions of the vulnerable app, potentially leading to the exposure of sensitive information. An attacker can create a malicious app that hijacks the legitimate Inure app, intercepting and stealing sensitive information when installed on the victim's device. This issue affects all Android versions before Android 11.

## References
- https://huntr.com/bounties/2108644e-9e54-4236-932d-f204fc68b607
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/0xxx/CVE-2024-0245.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-0245
- https://github.com/hamza417/inure/commit/a0c3e68b0542bcd7007c93618e0d50a5331de061
