# [M] Net::CIDR::Set versions 0.10 through 0.13 for Perl does not properly consider leading zero characters in IP CIDR address strings, which could allow attackers to bypass access control that is based on IP addresses

## Summary
Severity: Medium
Advisory: CVE-2025-40911
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2025-05-27
Source: https://osv.dev/vulnerability/CVE-2025-40911
Type: osv

## Details
Net::CIDR::Set versions 0.10 through 0.13 for Perl does not properly handle leading zero characters in IP CIDR address strings, which could allow attackers to bypass access control that is based on IP addresses.

Leading zeros are used to indicate octal numbers, which can confuse users who are intentionally using octal notation, as well as users who believe they are using decimal notation.

Net::CIDR::Set used code from Net::CIDR::Lite, which had a similar vulnerability CVE-2021-47154.

## References
- https://cpan.org/modules
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40911.json
- https://metacpan.org/release/RRWO/Net-CIDR-Set-0.14/changes
- https://nvd.nist.gov/vuln/detail/CVE-2025-40911
- https://github.com/robrwo/perl-Net-CIDR-Set/commit/be7d91e8446ad8013b08b4be313d666dab003a8a.patch
- https://github.com/robrwo/perl-Net-CIDR-Set
- https://blog.urth.org/2021/03/29/security-issues-in-perl-ip-address-distros/
