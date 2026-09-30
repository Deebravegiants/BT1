# [H] CVE-2021-29662

## Summary
Severity: High
Advisory: CVE-2021-29662
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2021-03-31
Source: https://osv.dev/vulnerability/CVE-2021-29662
Type: osv

## Details
The Data::Validate::IP module through 0.29 for Perl does not properly consider extraneous zero characters at the beginning of an IP address string, which (in some situations) allows attackers to bypass access control that is based on IP addresses.

## References
- https://security.netapp.com/advisory/ntap-20210604-0002/
- https://github.com/houseabsolute/Data-Validate-IP/commit/3bba13c819d616514a75e089badd75002fd4f14e
- https://github.com/houseabsolute/Data-Validate-IP
- https://blog.urth.org/2021/03/29/security-issues-in-perl-ip-address-distros/
- https://github.com/sickcodes/security/blob/master/advisories/SICK-2021-018.md
- https://sick.codes/sick-2021-018/
