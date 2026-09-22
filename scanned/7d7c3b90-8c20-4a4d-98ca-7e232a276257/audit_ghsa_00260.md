# [H] JSNAPy allows unprivileged local users to alter files under the directory

## Summary
Severity: High
Advisory: GHSA-qc55-vm3j-74gp
CVE: CVE-2018-0023
CWE: CWE-276
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2018-07-12
Source: https://github.com/advisories/GHSA-qc55-vm3j-74gp
Type: github-advisory

## Affected
- PyPI: `jsnapy` — affected >=0 <1.3.0

## Details
JSNAPy is an open source python version of Junos Snapshot Administrator developed by Juniper available through github. The default configuration and sample files of JSNAPy automation tool versions prior to 1.3.0 are created world writable. This insecure file and directory permission allows unprivileged local users to alter the files under this directory including inserting operations not intended by the package maintainer, system administrator, or other users. This issue only affects users who downloaded and installed JSNAPy from github.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-0023
- https://github.com/Juniper/jsnapy
- https://github.com/advisories/GHSA-qc55-vm3j-74gp
- https://github.com/pypa/advisory-database/tree/main/vulns/jsnapy/PYSEC-2018-84.yaml
- https://kb.juniper.net/JSA10856
- https://web.archive.org/web/20200227125151/http://www.securityfocus.com/bid/103745
