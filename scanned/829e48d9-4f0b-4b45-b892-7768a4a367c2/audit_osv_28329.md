# [M] CVE-2024-31573

## Summary
Severity: Medium
Advisory: CVE-2024-31573
Aliases: GHSA-chfm-68vv-pvw5
CVSS: 4.0 (CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2025-10-17
Source: https://osv.dev/vulnerability/CVE-2024-31573
Type: osv

## Details
XMLUnit for Java before 2.10.0, in the default configuration, might allow code execution via an untrusted stylesheet (used for an XSLT transformation), because XSLT extension functions are enabled.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/31xxx/CVE-2024-31573.json
- https://github.com/advisories/GHSA-chfm-68vv-pvw5
- https://nvd.nist.gov/vuln/detail/CVE-2024-31573
- https://github.com/xmlunit/xmlunit/issues/264
- https://github.com/xmlunit/xmlunit/commit/b81d48b71dfd2868bdfc30a3e17ff973f32bc15b
