# [M] capacitor-updater - End-to-End Encryption Bypass via Private Key Distribution

## Summary
Severity: Medium
Advisory: CVE-2026-56254
Aliases: GHSA-j2f4-4pfc-p8rx
CVSS: 6.0 (CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:N/VC:L/VI:H/VA:L/SC:N/SI:N/SA:N)
Published: 2026-07-10
Source: https://osv.dev/vulnerability/CVE-2026-56254
Type: osv

## Details
In @capgo/capacitor-updater (Cap-go/capgo) before 12.128.2, the end-to-end encryption scheme distributes the private key to each device that downloads the app. Because the public key can be derived from the private key, an attacker performing a man-in-the-middle attack or compromising the Capgo server can create a validly signed update bundle and cause devices to install an update not produced by the original app maker.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/56xxx/CVE-2026-56254.json
- https://github.com/Cap-go/capgo/security/advisories/GHSA-j2f4-4pfc-p8rx
- https://nvd.nist.gov/vuln/detail/CVE-2026-56254
- https://www.vulncheck.com/advisories/capacitor-updater-end-to-end-encryption-bypass-via-private-key-distribution
