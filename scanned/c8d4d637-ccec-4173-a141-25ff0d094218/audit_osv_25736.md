# [M] SSH public key login without private key challenge if mfa is enabled in jumpserver

## Summary
Severity: Medium
Advisory: CVE-2023-42818
Aliases: GHSA-jv3c-27cv-w8jv, GO-2025-3570
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:L)
Published: 2023-09-27
Source: https://osv.dev/vulnerability/CVE-2023-42818
Type: osv

## Details
JumpServer is an open source bastion host. When users enable MFA and use a public key for authentication, the Koko SSH server does not verify the corresponding SSH private key. An attacker could exploit a vulnerability by utilizing a disclosed public key to attempt brute-force authentication against the SSH service This issue has been patched in versions 3.6.5 and 3.5.6. Users are advised to upgrade. There are no known workarounds for this issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/42xxx/CVE-2023-42818.json
- https://github.com/jumpserver/jumpserver/security/advisories/GHSA-jv3c-27cv-w8jv
- https://nvd.nist.gov/vuln/detail/CVE-2023-42818
- https://www.sonarsource.com/blog/diving-into-jumpserver-attackers-gateway-to-internal-networks-1-2
