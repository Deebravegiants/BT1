# [M] CUPS has an integer underflow in `_ppdCreateFromIPP` causes root cupsd crash via negative `job-password-supported`

## Summary
Severity: Medium
Advisory: CVE-2026-39314
Aliases: GHSA-pp8w-2g52-7vj7
CVSS: 4.0 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2026-04-07
Source: https://osv.dev/vulnerability/CVE-2026-39314
Type: osv

## Details
OpenPrinting CUPS is an open source printing system for Linux and other Unix-like operating systems. In versions 2.4.16 and prior, an integer underflow vulnerability in _ppdCreateFromIPP() (cups/ppd-cache.c) allows any unprivileged local user to crash the cupsd root process by supplying a negative job-password-supported IPP attribute. The bounds check only caps the upper bound, so a negative value passes validation, is cast to size_t (wrapping to ~2^64), and is used as the length argument to memset() on a 33-byte stack buffer. This causes an immediate SIGSEGV in the cupsd root process. Combined with systemd's Restart=on-failure, an attacker can repeat the crash for sustained denial of service.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/39xxx/CVE-2026-39314.json
- https://github.com/OpenPrinting/cups/security/advisories/GHSA-pp8w-2g52-7vj7
- https://nvd.nist.gov/vuln/detail/CVE-2026-39314
