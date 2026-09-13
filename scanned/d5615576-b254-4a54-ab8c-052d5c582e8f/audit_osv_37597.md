# [M] xrdp: RDP MAC signature (dataSignature) never verified on receive — integrity bypass in non-TLS mode

## Summary
Severity: Medium
Advisory: CVE-2026-32105
Aliases: GHSA-j2jm-c596-c5q3
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:L/SC:H/SI:H/SA:L)
Published: 2026-04-17
Source: https://osv.dev/vulnerability/CVE-2026-32105
Type: osv

## Details
xrdp is an open source RDP server. In versions through 0.10.5, xrdp does not implement verification for the Message Authentication Code (MAC) signature of encrypted RDP packets when using the "Classic RDP Security" layer. While the sender correctly generates signatures, the receiving logic lacks the necessary implementation to validate the 8-byte integrity signature, causing it to be silently ignored. An unauthenticated attacker with man-in-the-middle (MITM) capabilities can exploit this missing check to modify encrypted traffic in transit without detection. It does not affect connections where the TLS security layer is enforced. This issue has been fixed in version 0.10.6. If users are unable to immediately upgrade, they should configure xrdp.ini to enforce TLS security (security_layer=tls) to ensure end-to-end integrity.

## References
- https://github.com/neutrinolabs/xrdp/releases/tag/v0.10.6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/32xxx/CVE-2026-32105.json
- https://github.com/neutrinolabs/xrdp/security/advisories/GHSA-j2jm-c596-c5q3
- https://nvd.nist.gov/vuln/detail/CVE-2026-32105
