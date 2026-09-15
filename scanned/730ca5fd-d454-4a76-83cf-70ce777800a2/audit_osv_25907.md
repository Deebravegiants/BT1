# [H] Perl: perl for windows binary hijacking vulnerability

## Summary
Severity: High
Advisory: CVE-2023-47039
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-01-02
Source: https://osv.dev/vulnerability/CVE-2023-47039
Type: osv

## Details
A vulnerability was found in Perl. This security issue occurs while Perl for Windows relies on the system path environment variable to find the shell (`cmd.exe`). When running an executable that uses the Windows Perl interpreter, Perl attempts to find and execute `cmd.exe` within the operating system. However, due to path search order issues, Perl initially looks for cmd.exe in the current working directory. This flaw allows an attacker with limited privileges to place`cmd.exe` in locations with weak permissions, such as `C:\ProgramData`. By doing so, arbitrary code can be executed when an administrator attempts to use this executable from these compromised locations.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=1056746
- https://perldoc.perl.org/perl5382delta#CVE-2023-47039-Perl-for-Windows-binary-hijacking-vulnerability
- https://access.redhat.com/security/cve/CVE-2023-47039
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/47xxx/CVE-2023-47039.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-47039
- https://security.netapp.com/advisory/ntap-20240208-0005/
- https://bugzilla.redhat.com/show_bug.cgi?id=2249525
- https://github.com/Perl/perl5
