# [H] iccDEV has a null pointer dereference in CIccTagXmlStruct::ParseTag()

## Summary
Severity: High
Advisory: CVE-2026-31792
Aliases: GHSA-j3mh-rjg5-8gw7
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-03-10
Source: https://osv.dev/vulnerability/CVE-2026-31792
Type: osv

## Details
iccDEV provides a set of libraries and tools for working with ICC color management profiles. Prior to 2.3.1.5, there is a null pointer dereference in CIccTagXmlStruct::ParseTag() causing a segmentation fault or denial of service. This vulnerability is fixed in 2.3.1.5.

## References
- https://github.com/InternationalColorConsortium/iccDEV/releases/tag/v2.3.1.5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31792.json
- https://github.com/InternationalColorConsortium/iccDEV/security/advisories/GHSA-j3mh-rjg5-8gw7
- https://nvd.nist.gov/vuln/detail/CVE-2026-31792
- https://github.com/InternationalColorConsortium/iccDEV/issues/633
- https://github.com/InternationalColorConsortium/iccDEV/pull/639
