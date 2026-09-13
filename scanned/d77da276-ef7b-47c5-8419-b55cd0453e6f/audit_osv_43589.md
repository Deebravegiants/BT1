# [C] rxrpc: Fix UAF in rxgk_issue_challenge()

## Summary
Severity: Critical
Advisory: CVE-2026-74433
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74433
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.16.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

rxrpc: Fix UAF in rxgk_issue_challenge()

Fix rxgk_issue_challenge() to free the page containing the challenge
content after invoking the tracepoint as the whdr passed to the tracepoint
points into the page just freed.

## References
- https://git.kernel.org/stable/c/107a4cb0d47e735830f852d83970d5c81f8e1e08
- https://git.kernel.org/stable/c/83bb0ed050e2ad9453d8ef50e4d6e624eac6eed8
- https://git.kernel.org/stable/c/844b8525ce503405c462ad67f750bec648720397
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74433.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74433
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
