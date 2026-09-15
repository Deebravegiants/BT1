# [M] Sunshine clickjacking in the UI leads to unauthorized actions being performed

## Summary
Severity: Medium
Advisory: CVE-2025-53096
Aliases: GHSA-x97g-h2vp-g2c5
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:L)
Published: 2025-07-01
Source: https://osv.dev/vulnerability/CVE-2025-53096
Type: osv

## Details
Sunshine is a self-hosted game stream host for Moonlight. Prior to version 2025.628.4510, the web UI of Sunshine lacks protection against Clickjacking attacks. This vulnerability allows an attacker to embed the Sunshine interface within a malicious website using an invisible or disguised iframe. If a user is tricked into interacting (one or multiple clicks) with the malicious page while authenticated, they may unknowingly perform actions within the Sunshine application without their consent. This issue has been patched in version 2025.628.4510.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/53xxx/CVE-2025-53096.json
- https://github.com/LizardByte/Sunshine/security/advisories/GHSA-x97g-h2vp-g2c5
- https://nvd.nist.gov/vuln/detail/CVE-2025-53096
- https://github.com/LizardByte/Sunshine/commit/2f27a57d01911436017f87bf08b9e36dcfaa86cc
