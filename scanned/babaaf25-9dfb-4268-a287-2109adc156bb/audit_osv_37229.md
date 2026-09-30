# [H] CVE-2026-29954

## Summary
Severity: High
Advisory: CVE-2026-29954
CVSS: 7.6 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:L/A:N)
Published: 2026-03-30
Source: https://osv.dev/vulnerability/CVE-2026-29954
Type: osv

## Details
In KubePlus 4.1.4, the mutating webhook and kubeconfiggenerator components have an SSRF vulnerability when processing the chartURL field of ResourceComposition resources. The field is only URL-encoded without validating the target address. More critically, when kubeconfiggenerator uses wget to download charts, the chartURL is directly concatenated into the command, allowing attackers to inject wget's `--header` option to achieve arbitrary HTTP header injection.

## References
- https://gist.github.com/b0b0haha/33baea60fd2a847f11f1fb02e43c64c0
- https://github.com/b0b0haha/CVE-2026-29954/blob/main/README.md
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/29xxx/CVE-2026-29954.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-29954
