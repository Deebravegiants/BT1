# [C] Apache CXF: Self-issued ID token claims validation skipped

## Summary
Severity: Critical
Advisory: CVE-2026-65583
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-08-06
Source: https://osv.dev/vulnerability/CVE-2026-65583
Type: osv

## Details
Apache CXF’s OIDC relying-party token validation could accept self-issued ID tokens without enforcing required claim checks (issuer/subject/audience/time and sub_jwk binding), enabling authentication bypass with crafted tokens. However, note that self-issued ID tokens are not accepted by default in the validator. Users are recommended to upgrade to versions 4.2.3 or 4.1.8 or 3.6.12, which fixes this issue.

## References
- http://www.openwall.com/lists/oss-security/2026/08/06/23
- https://repo.maven.apache.org/maven2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/65xxx/CVE-2026-65583.json
- https://lists.apache.org/thread/fzj8yzgfl53gclxrcdrnrx3grcpkq51j
- https://nvd.nist.gov/vuln/detail/CVE-2026-65583
