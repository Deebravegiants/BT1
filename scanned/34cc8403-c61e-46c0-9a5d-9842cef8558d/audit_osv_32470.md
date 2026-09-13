# [M] Sub::HandlesVia for Perl allows untrusted code to be included from the current working directory

## Summary
Severity: Medium
Advisory: CVE-2025-30673
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2025-04-01
Source: https://osv.dev/vulnerability/CVE-2025-30673
Type: osv

## Details
Sub::HandlesVia for Perl before 0.050002 allows untrusted code from the current working directory ('.') to be loaded similar to CVE-2016-1238.

If an attacker can place a malicious file in current working directory, it may be loaded instead of the intended file, potentially leading to arbitrary code execution.

Sub::HandlesVia uses Mite to produce the affected code section due to CVE-2025-30672

## References
- https://cpan.org/modules
- https://metacpan.org/dist/Sub-HandlesVia/changes#L12
- https://metacpan.org/release/TOBYINK/Sub-HandlesVia-0.050001/source/lib/Sub/HandlesVia/Mite.pm#L114
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/30xxx/CVE-2025-30673.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-30673
- https://github.com/tobyink/p5-sub-handlesvia
- https://blogs.perl.org/users/todd_rinaldo/2016/11/what-happened-to-dot-in-inc.html
