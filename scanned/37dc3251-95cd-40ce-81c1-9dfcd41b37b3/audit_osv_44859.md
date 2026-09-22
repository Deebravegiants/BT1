# [M] Open WebUI: Inaccessible knowledge bases are exposed through the built-in knowledge tool on most vector backends

## Summary
Severity: Medium
Advisory: CVE-2026-87017
Aliases: GHSA-pcvc-8vrv-8q6w
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-09-09
Source: https://osv.dev/vulnerability/CVE-2026-87017
Type: osv

## Details
Open WebUI is an extensible, feature-rich, and user-friendly self-hosted AI platform. From 0.7.0 until 0.11.1, the built-in knowledge search tool passed the caller's readable knowledge identifiers through a metadata filter, but the search methods in eleven shipped vector backends ignored that filter. An authenticated user on an affected backend could enumerate the identifiers, names, and descriptions of inaccessible knowledge bases from the shared collection, although the associated document text remained in separate collections. This issue is fixed in version 0.11.1.

## References
- https://github.com/open-webui/open-webui/releases/tag/v0.11.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/87xxx/CVE-2026-87017.json
- https://github.com/open-webui/open-webui/security/advisories/GHSA-pcvc-8vrv-8q6w
- https://nvd.nist.gov/vuln/detail/CVE-2026-87017
- https://github.com/open-webui/open-webui/commit/1d6d4e6e6647e1d403438ede7bd9ba20bc4cc8f6
