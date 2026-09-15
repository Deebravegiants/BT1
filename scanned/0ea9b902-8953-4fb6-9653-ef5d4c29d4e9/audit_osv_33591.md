# [M] File Descriptor Exhaustion in sslh-select and sslh-ev triggers SEGFAULT

## Summary
Severity: Medium
Advisory: CVE-2025-46807
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2025-06-02
Source: https://osv.dev/vulnerability/CVE-2025-46807
Type: osv

## Details
A Allocation of Resources Without Limits or Throttling vulnerability in sslh allows attackers to easily exhaust the file descriptors in sslh and deny legitimate users service.This issue affects sslh before 2.2.4.

## References
- https://github.com/yrutschle/sslh/releases/tag/v2.2.4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/46xxx/CVE-2025-46807.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-46807
- https://bugzilla.suse.com/show_bug.cgi?id=CVE-2025-46807
