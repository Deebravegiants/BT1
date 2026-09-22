# [H] Suricata is vulnerable to a null deref when used with base64_data

## Summary
Severity: High
Advisory: CVE-2025-64335
Aliases: GHSA-v299-h7p3-q4f2
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-11-26
Source: https://osv.dev/vulnerability/CVE-2025-64335
Type: osv

## Details
Suricata is a network IDS, IPS and NSM engine developed by the OISF (Open Information Security Foundation) and the Suricata community. In versions from 8.0.0 to before 8.0.2, a NULL dereference can occur when the entropy keyword is used in conjunction with base64_data. This issue has been patched in version 8.0.2. A workaround involves disabling rules that use entropy in conjunction with base64_data.

## References
- https://www.vicarius.io/vsociety/posts/cve-2025-64335-detect-suricata-vulnerability
- https://www.vicarius.io/vsociety/posts/cve-2025-64335-mitigate-suricata-vulnerability
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/64xxx/CVE-2025-64335.json
- https://github.com/OISF/suricata/security/advisories/GHSA-v299-h7p3-q4f2
- https://nvd.nist.gov/vuln/detail/CVE-2025-64335
- https://github.com/OISF/suricata/commit/c935f08cd988600fd0a4f828a585b181dd5de012
