# [M] Bulwark Webmail S/MIME signature verification accepted self-signed certificates

## Summary
Severity: Medium
Advisory: CVE-2026-35389
Aliases: GHSA-v6w6-338p-p256
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-04-06
Source: https://osv.dev/vulnerability/CVE-2026-35389
Type: osv

## Details
Bulwark Webmail is a self-hosted webmail client for Stalwart Mail Server. Prior to 1.4.11, S/MIME signature verification did not validate the certificate trust chain (checkChain: false). Any email signed with a self-signed or untrusted certificate was displayed as having a valid signature. This vulnerability is fixed in 1.4.11.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/35xxx/CVE-2026-35389.json
- https://github.com/bulwarkmail/webmail/security/advisories/GHSA-v6w6-338p-p256
- https://nvd.nist.gov/vuln/detail/CVE-2026-35389
