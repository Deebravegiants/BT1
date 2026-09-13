# [H] CVE-2019-9628

## Summary
Severity: High
Advisory: CVE-2019-9628
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-04-11
Source: https://osv.dev/vulnerability/CVE-2019-9628
Type: osv

## Details
The XMLTooling library all versions prior to V3.0.4, provided with the OpenSAML and Shibboleth Service Provider software, contains an XML parsing class. Invalid data in the XML declaration causes an exception of a type that was not handled properly in the parser class and propagates an unexpected exception type.

## References
- https://usn.ubuntu.com/3921-1/
- https://wiki.shibboleth.net/confluence/display/SP3/SecurityAdvisories
- http://lists.opensuse.org/opensuse-security-announce/2019-04/msg00079.html
- http://lists.opensuse.org/opensuse-security-announce/2019-04/msg00095.html
- https://security.netapp.com/advisory/ntap-20190611-0003/
- https://shibboleth.net/community/advisories/secadv_20190311.txt
- https://bugs.launchpad.net/ubuntu/+source/xmltooling/+bug/1819912
