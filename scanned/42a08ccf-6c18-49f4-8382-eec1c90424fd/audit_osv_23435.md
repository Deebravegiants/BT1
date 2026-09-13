# [H] mctp: fix use after free

## Summary
Severity: High
Advisory: CVE-2022-48782
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-07-16
Source: https://osv.dev/vulnerability/CVE-2022-48782
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.16.0 <5.16.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

mctp: fix use after free

Clang static analysis reports this problem
route.c:425:4: warning: Use of memory after it is freed
  trace_mctp_key_acquire(key);
  ^~~~~~~~~~~~~~~~~~~~~~~~~~~
When mctp_key_add() fails, key is freed but then is later
used in trace_mctp_key_acquire().  Add an else statement
to use the key only when mctp_key_add() is successful.

## References
- https://git.kernel.org/stable/c/1dd3ecbec5f606b2a526c47925c8634b1a6bb81e
- https://git.kernel.org/stable/c/7e5b6a5c8c44310784c88c1c198dde79f6402f7b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/48xxx/CVE-2022-48782.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-48782
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
