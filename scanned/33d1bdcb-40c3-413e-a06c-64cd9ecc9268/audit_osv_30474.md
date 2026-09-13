# [M] drm/i915/hdcp: Add encoder check in hdcp2_get_capability

## Summary
Severity: Medium
Advisory: CVE-2024-53050
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-11-19
Source: https://osv.dev/vulnerability/CVE-2024-53050
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.7.0 <6.11.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/i915/hdcp: Add encoder check in hdcp2_get_capability

Add encoder check in intel_hdcp2_get_capability to avoid
null pointer error.

## References
- https://git.kernel.org/stable/c/5b89dcf23575eb5bb95ce8d672cbc2232c2eb096
- https://git.kernel.org/stable/c/d34f4f058edf1235c103ca9c921dc54820d14d40
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/53xxx/CVE-2024-53050.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-53050
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
