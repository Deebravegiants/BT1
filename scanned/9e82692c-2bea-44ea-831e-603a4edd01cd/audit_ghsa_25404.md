# [H] Apache Guacamole Race Condition vulnerability

## Summary
Severity: High
Advisory: GHSA-3vv3-585q-wv6x
CVE: CVE-2017-3158
CWE: CWE-362
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-3vv3-585q-wv6x
Type: github-advisory

## Affected
- Maven: `org.apache.guacamole:guacamole-common` — affected >=0.9.5 <0.9.11-incubating

## Details
A race condition in Guacamole's terminal emulator in versions 0.9.5 through 0.9.10-incubating could allow writes of blocks of printed data to overlap. Such overlapping writes could cause packet data to be misread as the packet length, resulting in the remaining data being written beyond the end of a statically-allocated buffer.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-3158
- https://lists.apache.org/thread.html/b218d36bfdaf655d27382daec4dcd02ec717631f4aee8b7e4300ad65@%3Cuser.guacamole.apache.org%3E
