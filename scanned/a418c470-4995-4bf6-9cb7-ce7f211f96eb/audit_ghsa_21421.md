# [C] Apache Ivy does not verify target path when extracting the archive

## Summary
Severity: Critical
Advisory: GHSA-94rr-4jr5-9h2p
CVE: CVE-2022-37865
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2022-11-07
Source: https://github.com/advisories/GHSA-94rr-4jr5-9h2p
Type: github-advisory

## Affected
- Maven: `org.apache.ivy:ivy` — affected >=2.4.0 <2.5.1

## Details
With Apache Ivy 2.4.0 an optional packaging attribute has been introduced that allows artifacts to be unpacked on the fly if they used
pack200 or zip packaging.

For artifacts using the "zip", "jar" or "war" packaging Ivy prior to version 2.5.1 doesn't verify the target path when extracting the archive. An archive containing absolute paths or paths that try to traverse "upwards" using ".." sequences can then write files to any location on
the local fie system that the user executing Ivy has write access to.

Ivy users of version 2.4.0 to 2.5.0 should upgrade to Ivy version 2.5.1.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-37865
- https://lists.apache.org/thread/gqvvv7qsm2dfjg6xzsw1s2h08tbr0sdy
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/YDIFDL5WSBEKBUVKTABUFDDD25SBNJLS
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/YDIFDL5WSBEKBUVKTABUFDDD25SBNJLS
