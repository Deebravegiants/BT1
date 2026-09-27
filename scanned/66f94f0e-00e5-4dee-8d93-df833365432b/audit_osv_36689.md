# [H] Apache CloudStack: Unauthenticated Command Injection in Direct Download Templates

## Summary
Severity: High
Advisory: CVE-2026-25077
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-08
Source: https://osv.dev/vulnerability/CVE-2026-25077
Type: osv

## Details
Account users are allowed by default to register templates to be downloaded directly to the primary storage for deploying instances using the KVM hypervisor. Due to missing file name sanitization, an attacker can register malicious templates to execute arbitrary code on the KVM hosts. This can result in the compromise of resource integrity and confidentiality, data loss, denial of service, and availability of the KVM-based infrastructure managed by CloudStack.


Users are recommended to upgrade to Apache CloudStack versions 4.20.3.0 or 4.22.0.1, or later, which fixes this issue.

## References
- http://www.openwall.com/lists/oss-security/2026/05/09/6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/25xxx/CVE-2026-25077.json
- https://lists.apache.org/thread/n8mt5b7wkpysstb8w7rr9f02kc5cq2xm
- https://nvd.nist.gov/vuln/detail/CVE-2026-25077
