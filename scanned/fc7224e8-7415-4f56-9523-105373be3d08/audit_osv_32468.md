# [M] Linux::Statm::Tiny for Perl allows untrusted code to be included from the current working directory

## Summary
Severity: Medium
Advisory: CVE-2025-3051
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2025-04-01
Source: https://osv.dev/vulnerability/CVE-2025-3051
Type: osv

## Details
Linux::Statm::Tiny for Perl before 0.0701 allows untrusted code from the current working directory ('.') to be loaded similar to CVE-2016-1238.

If an attacker can place a malicious file in current working directory, it may be loaded instead of the intended file, potentially leading to arbitrary code execution.

Linux::Statm::Tiny uses Mite to produce the affected code section due to CVE-2025-30672

## References
- https://cpan.org/modules
- https://metacpan.org/release/RRWO/Linux-Statm-Tiny-0.0700/source/lib/Linux/Statm/Tiny/Mite.pm#L82
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/3xxx/CVE-2025-3051.json
- https://metacpan.org/release/RRWO/Linux-Statm-Tiny-0.0701/changes
- https://nvd.nist.gov/vuln/detail/CVE-2025-3051
- https://github.com/robrwo/Linux-Statm-Tiny
- https://blogs.perl.org/users/todd_rinaldo/2016/11/what-happened-to-dot-in-inc.html
