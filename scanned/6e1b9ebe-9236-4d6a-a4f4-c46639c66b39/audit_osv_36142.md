# [M] iccDEV is Vulnerable to Null Pointer Dereference in CIccProfileXml::ParseBasic() Leading to Denial of Service

## Summary
Severity: Medium
Advisory: CVE-2026-21506
Aliases: GHSA-wfm7-m548-x4vp
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-01-07
Source: https://osv.dev/vulnerability/CVE-2026-21506
Type: osv

## Details
iccDEV provides a set of libraries and tools that allow for the interaction, manipulation, and application of ICC color management profiles. Prior to version 2.3.1.2, iccDEV is vulnerable to Null pointer dereference in CIccProfileXml::ParseBasic(), leading to denial of service. This issue has been patched in version 2.3.1.2.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/21xxx/CVE-2026-21506.json
- https://github.com/InternationalColorConsortium/iccDEV/security/advisories/GHSA-wfm7-m548-x4vp
- https://nvd.nist.gov/vuln/detail/CVE-2026-21506
- https://github.com/InternationalColorConsortium/iccDEV/issues/371
- https://github.com/InternationalColorConsortium/iccDEV/commit/f2ea32372ad3ebbd29147940229cb9c5548fe033
- https://github.com/InternationalColorConsortium/iccDEV/pull/418
