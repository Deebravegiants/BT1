# [M] Kratos has a Confused Deputy issue

## Summary
Severity: Medium
Advisory: GHSA-jj45-xvq5-rhh9
CVE: CVE-2026-6993
CWE: CWE-441
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-04-25
Source: https://github.com/advisories/GHSA-jj45-xvq5-rhh9
Type: github-advisory

## Affected
- Go: `github.com/go-kratos/kratos/v2` — affected >=0

## Details
A security flaw has been discovered in go-kratos kratos up to 2.9.2. This impacts the function NewServer of the file transport/http/server.go of the component http.DefaultServeMux Fallback Handler. The manipulation results in unintended intermediary. The attack may be launched remotely. The exploit has been released to the public and may be used for attacks. The patch is identified as 0284a5bcf92b5a7ee015300ce3051baf7ae4718d. Applying a patch is advised to resolve this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-6993
- https://github.com/go-kratos/kratos/issues/3810
- https://github.com/go-kratos/kratos/pull/3814
- https://github.com/Yanhu007/kratos/commit/0284a5bcf92b5a7ee015300ce3051baf7ae4718d
- https://github.com/go-kratos/kratos
- https://vuldb.com/submit/797099
- https://vuldb.com/vuln/359545
- https://vuldb.com/vuln/359545/cti
