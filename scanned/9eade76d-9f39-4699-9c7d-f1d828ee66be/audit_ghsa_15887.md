# [H] Apache Commons IO: Possible denial of service attack on untrusted input to XmlStreamReader

## Summary
Severity: High
Advisory: GHSA-78wr-2p64-hpwj
CVE: CVE-2024-47554
CWE: CWE-400
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-10-03
Source: https://github.com/advisories/GHSA-78wr-2p64-hpwj
Type: github-advisory

## Affected
- Maven: `commons-io:commons-io` — affected >=2.0 <2.14.0

## Details
Uncontrolled Resource Consumption vulnerability in Apache Commons IO.

The `org.apache.commons.io.input.XmlStreamReader` class may excessively consume CPU resources when processing maliciously crafted input.


This issue affects Apache Commons IO: from 2.0 before 2.14.0.

Users are recommended to upgrade to version 2.14.0 or later, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-47554
- https://github.com/apache/commons-io
- https://lists.apache.org/thread/6ozr91rr9cj5lm0zyhv30bsp317hk5z1
- https://security.netapp.com/advisory/ntap-20250131-0010
- http://www.openwall.com/lists/oss-security/2024/10/03/2
