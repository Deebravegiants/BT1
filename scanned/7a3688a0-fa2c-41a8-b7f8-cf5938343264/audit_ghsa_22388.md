# [M] OpenDaylight NULL Pointer Dereference

## Summary
Severity: Medium
Advisory: GHSA-gjq3-997p-hg6f
CVE: CVE-2017-1000360
CWE: CWE-476
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-gjq3-997p-hg6f
Type: github-advisory

## Affected
- Maven: `org.opendaylight.controller:releasepom` — affected >=0

## Details
StreamCorruptedException and NullPointerException in OpenDaylight odl-mdsal-xsql. Controller launches exceptions in the console. Component: OpenDaylight odl-mdsal-xsql is vulnerable to this flaw. Version: The tested versions are OpenDaylight 3.3 and 4.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-1000360
- https://aaltodoc.aalto.fi/bitstream/handle/123456789/21584/master_Bidaj_Andi_2016.pdf
