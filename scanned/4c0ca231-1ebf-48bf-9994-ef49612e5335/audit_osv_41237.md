# [M] GNU Wget 1.25.0 Heap Buffer Underread via Metalink URL Parsing

## Summary
Severity: Medium
Advisory: CVE-2026-58469
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-07
Source: https://osv.dev/vulnerability/CVE-2026-58469
Type: osv

## Details
GNU Wget through 1.25.0, fixed in commit 37a40fc, contains a heap buffer underread vulnerability in the clean_metalink_string() function within src/metalink.c that allows a malicious server to trigger memory corruption by serving a Metalink document containing a whitespace-only URL. Attackers can cause the function to decrement a pointer past the start of the buffer when processing an all-whitespace Metalink URL, potentially leading to abnormal program behavior.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/58xxx/CVE-2026-58469.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-58469
- https://www.vulncheck.com/advisories/gnu-wget-heap-buffer-underread-via-metalink-url-parsing
- https://gitlab.com/gnuwget/wget/-/commit/37a40fcb450153f69537c7cbc2a7a4fb0b6f7826
- https://gitlab.com/gnuwget/wget
