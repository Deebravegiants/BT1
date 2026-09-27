# [M] AddressSanitizer: stack-buffer-overflow in jq_fuzz_execute (jv_string_vfmt)

## Summary
Severity: Medium
Advisory: CVE-2025-48060
Aliases: GHSA-p7rr-28xf-3m5w
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:P)
Published: 2025-05-21
Source: https://osv.dev/vulnerability/CVE-2025-48060
Type: osv

## Details
jq is a command-line JSON processor. In versions up to and including 1.7.1, a heap-buffer-overflow is present in function `jv_string_vfmt` in the jq_fuzz_execute harness from oss-fuzz. This crash happens on file jv.c, line 1456 `void* p = malloc(sz);`. As of time of publication, no patched versions are available.

## References
- https://lists.debian.org/debian-lts-announce/2025/09/msg00022.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/48xxx/CVE-2025-48060.json
- https://github.com/jqlang/jq/security/advisories/GHSA-p7rr-28xf-3m5w
- https://nvd.nist.gov/vuln/detail/CVE-2025-48060
