# [H] App::Ack versions before 3.10.0 for Perl allow memory exhaustion via an unbounded context value in a project .ackrc

## Summary
Severity: High
Advisory: CVE-2026-49146
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-08
Source: https://osv.dev/vulnerability/CVE-2026-49146
Type: osv

## Details
App::Ack versions before 3.10.0 for Perl allow memory exhaustion via an unbounded context value in a project .ackrc.

ack searches up the directory hierarchy from the current directory for a project .ackrc and loads its options. The -B and -C context options accepted any positive integer, and ack sized the before-context buffer to that value, so a project .ackrc setting --before-context=100000000 made ack allocate a buffer of 100 million elements.

A project .ackrc committed to an untrusted repository can abort ack with an out-of-memory condition.

## References
- http://www.openwall.com/lists/oss-security/2026/07/08/8
- https://cpan.org/modules
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/49xxx/CVE-2026-49146.json
- https://metacpan.org/release/PETDANCE/ack-v3.10.0/source/Changes
- https://nvd.nist.gov/vuln/detail/CVE-2026-49146
- https://github.com/beyondgrep/ack3/commit/45ff5fe77dbd96f7332f31943102291f878f30b8.patch
- https://github.com/beyondgrep/ack3
