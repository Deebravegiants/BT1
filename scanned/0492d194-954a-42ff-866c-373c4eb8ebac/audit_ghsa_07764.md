# [M] funadmin exposes sensitive information via getMember function

## Summary
Severity: Medium
Advisory: GHSA-8hhx-xq9j-xwfj
CVE: CVE-2026-2894
CWE: CWE-200
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-02-22
Source: https://github.com/advisories/GHSA-8hhx-xq9j-xwfj
Type: github-advisory

## Affected
- Packagist: `funadmin/funadmin` — affected >=0

## Details
A vulnerability was identified in funadmin up to 7.1.0-rc4. Affected by this vulnerability is the function getMember of the file app/frontend/view/login/forget.html. Such manipulation leads to information disclosure. The attack may be launched remotely. The exploit is publicly available and might be used. The vendor was contacted early about this disclosure but did not respond in any way.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-2894
- https://github.com/I4m6da/CVE/issues/1
- https://github.com/funadmin/funadmin
- https://vuldb.com/?ctiid.347205
- https://vuldb.com/?id.347205
- https://vuldb.com/?submit.753969
