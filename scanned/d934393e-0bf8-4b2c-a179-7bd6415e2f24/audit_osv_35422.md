# [M] Polkit: xml policy file with a large number of nested elements may lead to out-of-bounds write

## Summary
Severity: Medium
Advisory: CVE-2025-7519
CVSS: 6.7 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-07-14
Source: https://osv.dev/vulnerability/CVE-2025-7519
Type: osv

## Details
A flaw was found in polkit. When processing an XML policy with 32 or more nested elements in depth, an out-of-bounds write can be triggered. This issue can lead to a crash or other unexpected behavior, and arbitrary code execution is not discarded. To exploit this flaw, a high-privilege account is needed as it's required to place the malicious policy file properly.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://www.freedesktop.org/software/polkit/releases/
- https://access.redhat.com/security/cve/CVE-2025-7519
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/7xxx/CVE-2025-7519.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-7519
- https://bugzilla.redhat.com/show_bug.cgi?id=2379675
- https://github.com/polkit-org/polkit/commit/107d3801361b9f9084f78710178e683391f1d245
- https://github.com/polkit-org/polkit/pull/570
