# [C] CVE-2018-1000828

## Summary
Severity: Critical
Advisory: CVE-2018-1000828
CVSS: 9.0 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2018-12-20
Source: https://osv.dev/vulnerability/CVE-2018-1000828
Type: osv

## Details
FrostWire version <= frostwire-desktop-6.7.4-build-272 contains a XML External Entity (XXE) vulnerability in Man in the middle on update that can result in Disclosure of confidential data, denial of service, SSRF, port scanning. This attack appear to be exploitable via Man in the middle the call to update the software.

## References
- https://0dd.zone/2018/10/28/frostwire-XXE-MitM/
- https://github.com/frostwire/frostwire/issues/829
