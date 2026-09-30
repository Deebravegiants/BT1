# [M] Apache CloudStack: Authenticated pre-validation SSRF in registerTemplate

## Summary
Severity: Medium
Advisory: CVE-2026-61422
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-08-21
Source: https://osv.dev/vulnerability/CVE-2026-61422
Type: osv

## Details
Authenticated pre-validation SSRF vulnerability in Apache CloudStack's template and ISO registration functionality.

When registering a template or ISO, CloudStack makes a live HTTP HEAD/GET call to determine file size for secondary storage usage-limit checks, and this happens before URL validation is performed. However, this does not pose a malicious template or ISO registration risk, as URL validation still occurs prior to the actual download by the Secondary Storage VM.This issue affects Apache CloudStack: in 4.20.3.0 and from 4.21.0.0 through 4.22.1.0.

Users are recommended to upgrade to version 4.20.3.1 or 4.22.1.1 or later, which fixes the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/61xxx/CVE-2026-61422.json
- https://lists.apache.org/thread/g6cwddtjrwbh1d56wjz4cfp3fzfm4kbc
- https://nvd.nist.gov/vuln/detail/CVE-2026-61422
