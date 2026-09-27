# [H] Perl: write past buffer end via illegal user-defined unicode property

## Summary
Severity: High
Advisory: CVE-2023-47038
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-12-18
Source: https://osv.dev/vulnerability/CVE-2023-47038
Type: osv

## Details
A vulnerability was found in perl 5.30.0 through 5.38.0. This issue occurs when a crafted regular expression is compiled by perl, which can allow an attacker controlled byte buffer overflow in a heap allocated buffer.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=1056746
- https://github.com/aquasecurity/trivy/discussions/8400
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/GNEEWAACXQCEEAKSG7XX2D5YDRWLCIZJ/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/UMDZZ4SCEW6FRWZDMXGAKZ35THTAWFG6/
- https://perldoc.perl.org/perl5382delta#CVE-2023-47038-Write-past-buffer-end-via-illegal-user-defined-Unicode-property
- https://ubuntu.com/security/CVE-2023-47100
- https://www.suse.com/security/cve/CVE-2023-47100.html
- https://access.redhat.com/errata/RHSA-2024:2228
- https://access.redhat.com/errata/RHSA-2024:3128
- https://access.redhat.com/security/cve/CVE-2023-47038
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/47xxx/CVE-2023-47038.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-47038
- https://bugzilla.redhat.com/show_bug.cgi?id=2249523
- https://github.com/Perl/perl5/commit/12c313ce49b36160a7ca2e9b07ad5bd92ee4a010
- https://github.com/Perl/perl5/commit/7047915eef37fccd93e7cd985c29fe6be54650b6
- https://github.com/Perl/perl5/commit/ff1f9f59360afeebd6f75ca1502f5c3ebf077da3
- https://github.com/Perl/perl5
