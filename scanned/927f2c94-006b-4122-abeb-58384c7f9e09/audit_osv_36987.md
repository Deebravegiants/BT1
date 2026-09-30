# [M] iccDEV has SIO in parse3DTable() at iccFromCube.cpp Line 218

## Summary
Severity: Medium
Advisory: CVE-2026-27691
Aliases: GHSA-4gfj-4cjh-53v5
CVSS: 6.2 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-02-25
Source: https://osv.dev/vulnerability/CVE-2026-27691
Type: osv

## Details
iccDEV provides a set of libraries and tools for working with ICC color management profiles. In versions up to and including 2.3.1.4, signed integer overflow in iccFromCube.cpp during multiplication triggers undefined behavior, potentially causing crashes or incorrect ICC profile generation when processing crafted/large cube inputs. Commit 43ae18dd69fc70190d3632a18a3af2f3da1e052a fixes the issue. No known workarounds are available.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/27xxx/CVE-2026-27691.json
- https://github.com/InternationalColorConsortium/iccDEV/security/advisories/GHSA-4gfj-4cjh-53v5
- https://nvd.nist.gov/vuln/detail/CVE-2026-27691
- https://github.com/InternationalColorConsortium/iccDEV/issues/607
- https://github.com/InternationalColorConsortium/iccDEV/commit/43ae18dd69fc70190d3632a18a3af2f3da1e052a
- https://github.com/InternationalColorConsortium/iccDEV/pull/611
