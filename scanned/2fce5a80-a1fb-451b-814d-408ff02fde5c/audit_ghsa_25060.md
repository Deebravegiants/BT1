# [M] Use of NullPointerException Catch to Detect NULL Pointer Dereference in Pymongo

## Summary
Severity: Medium
Advisory: GHSA-x33v-f3gp-gw2c
CVE: CVE-2013-2132
CWE: CWE-395
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-x33v-f3gp-gw2c
Type: github-advisory

## Affected
- PyPI: `pymongo` — affected >=0 <2.5.2

## Details
bson/_cbsonmodule.c in the mongo-python-driver (aka. pymongo) before 2.5.2, as used in MongoDB, allows context-dependent attackers to cause a denial of service (NULL pointer dereference and crash) via vectors related to decoding of an "invalid DBRef."

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-2132
- https://github.com/mongodb/mongo-python-driver/commit/a060c15ef87e0f0e72974c7c0e57fe811bbd06a2
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=710597
- https://github.com/mongodb/mongo-python-driver
- https://github.com/pypa/advisory-database/tree/main/vulns/pymongo/PYSEC-2013-30.yaml
- https://jira.mongodb.org/browse/PYTHON-532
- https://lists.opensuse.org/opensuse-updates/2013-06/msg00180.html
- https://seclists.org/oss-sec/2013/q2/447
- https://ubuntu.com/usn/usn-1897-1
- https://www.debian.org/security/2013/dsa-2705
