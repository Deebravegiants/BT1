# [M] Use After Free in gpac/gpac

## Summary
Severity: Medium
Advisory: CVE-2023-4679
CVSS: 5.9 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2024-11-15
Source: https://osv.dev/vulnerability/CVE-2023-4679
Type: osv

## Details
A use after free vulnerability exists in GPAC version 2.3-DEV-revrelease, specifically in the gf_filterpacket_del function in filter_core/filter.c at line 38. This vulnerability can lead to a double-free condition, which may cause the application to crash.

## References
- https://huntr.com/bounties/6f721ee7-8785-4c26-801e-f40fed3faaac
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/4xxx/CVE-2023-4679.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-4679
- https://github.com/gpac/gpac/commit/b68b3f0bf5c366e003221d78fd663a1d5514a876
