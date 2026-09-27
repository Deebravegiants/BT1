# [H] iccDEV is vulnerable to stack-buffer-overflow in icFixXml()

## Summary
Severity: High
Advisory: CVE-2026-25502
Aliases: GHSA-c2qq-jf7w-rm27
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-02-03
Source: https://osv.dev/vulnerability/CVE-2026-25502
Type: osv

## Details
iccDEV provides a set of libraries and tools that allow for the interaction, manipulation, and application of ICC color management profiles. Prior to version 2.3.1.2, stack-based buffer overflow in icFixXml() function when processing malformed ICC profiles, allows potential arbitrary code execution through crafted NamedColor2 tags. This issue has been patched in version 2.3.1.2.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/25xxx/CVE-2026-25502.json
- https://github.com/InternationalColorConsortium/iccDEV/security/advisories/GHSA-c2qq-jf7w-rm27
- https://nvd.nist.gov/vuln/detail/CVE-2026-25502
- https://github.com/InternationalColorConsortium/iccDEV/issues/537
- https://github.com/InternationalColorConsortium/iccDEV/commit/be5d7ec5cc137c084c08006aee8cd3ed378c7ac2
- https://github.com/InternationalColorConsortium/iccDEV/pull/545
