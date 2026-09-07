# [M] Exposure of Sensitive Information to an Unauthorized Actor in Undertow

## Summary
Severity: Medium
Advisory: GHSA-vf6r-mmhc-3xcm
CVE: CVE-2018-14642
CWE: CWE-200
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-vf6r-mmhc-3xcm
Type: github-advisory

## Affected
- Maven: `io.undertow:undertow-core` — affected >=0 <2.0.19.FINAL

## Details
An information leak vulnerability was found in Undertow. If all headers are not written out in the first write() call then the code that handles flushing the buffer will always write out the full contents of the writevBuffer buffer, which may contain data from previous requests.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-14642
- https://access.redhat.com/errata/RHSA-2019:0362
- https://access.redhat.com/errata/RHSA-2019:0364
- https://access.redhat.com/errata/RHSA-2019:0365
- https://access.redhat.com/errata/RHSA-2019:0380
- https://access.redhat.com/errata/RHSA-2019:1106
- https://access.redhat.com/errata/RHSA-2019:1107
- https://access.redhat.com/errata/RHSA-2019:1108
- https://access.redhat.com/errata/RHSA-2019:1140
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-14642
