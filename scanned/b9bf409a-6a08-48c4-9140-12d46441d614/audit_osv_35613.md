# [H] Config::IniFiles versions before 3.001000 for Perl allow OS command injection and file overwrite via a 2-arg open() of the -file argument in _make_filehandle

## Summary
Severity: High
Advisory: CVE-2026-11527
CVSS: 8.6 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H)
Published: 2026-06-14
Source: https://osv.dev/vulnerability/CVE-2026-11527
Type: osv

## Details
Config::IniFiles versions before 3.001000 for Perl allow OS command injection and file overwrite via a 2-arg open() of the -file argument in _make_filehandle.

Config::IniFiles::_make_filehandle opens a filename argument with Perl's 2-arg open(), so a filename that begins or ends with a pipe ("| cmd", "cmd |") or begins with a redirect ("> path", ">> path") is run as a command or redirect rather than opened as a file. The helper is the open path behind the documented -file argument: new(-file => $thing) reaches it through ReadConfig. An in-memory scalar reference (-file => \$text) does not open a path and is unaffected.

Any caller that forwards untrusted input to the -file argument can run an arbitrary command or truncate a file under the process UID.

## References
- http://www.openwall.com/lists/oss-security/2026/06/14/5
- https://cpan.org/modules
- https://lists.debian.org/debian-lts-announce/2026/06/msg00026.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/11xxx/CVE-2026-11527.json
- https://metacpan.org/release/SHLOMIF/Config-IniFiles-3.001000/changes
- https://nvd.nist.gov/vuln/detail/CVE-2026-11527
- https://github.com/shlomif/perl-Config-IniFiles/commit/3e48f9627fbba4dae5de35be1f735cdeb7e47fb8.patch
- https://github.com/shlomif/perl-Config-IniFiles
