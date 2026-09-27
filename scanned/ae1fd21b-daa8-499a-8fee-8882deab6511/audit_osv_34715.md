# [H] Suricata is vulnerable to a stack overflow on large file transfers with http-body-printable

## Summary
Severity: High
Advisory: CVE-2025-64331
Aliases: GHSA-v32w-j79x-pfj2
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-11-26
Source: https://osv.dev/vulnerability/CVE-2025-64331
Type: osv

## Details
Suricata is a network IDS, IPS and NSM engine developed by the OISF (Open Information Security Foundation) and the Suricata community. Prior to versions 7.0.13 and 8.0.2, a stack overflow can occur on large HTTP file transfers if the user has increased the HTTP response body limit and enabled the logging of printable http bodies. This issue has been patched in versions 7.0.13 and 8.0.2. A workaround for this issue involves using default HTTP response body limits and/or disabling http-body-printable logging; body logging is disabled by default.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/64xxx/CVE-2025-64331.json
- https://github.com/OISF/suricata/security/advisories/GHSA-v32w-j79x-pfj2
- https://nvd.nist.gov/vuln/detail/CVE-2025-64331
