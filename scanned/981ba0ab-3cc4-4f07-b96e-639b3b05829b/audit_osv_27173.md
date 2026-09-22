# [C] Rsync: heap buffer overflow in rsync due to improper checksum length handling

## Summary
Severity: Critical
Advisory: CVE-2024-12084
Aliases: CVE-2024-12085, CVE-2024-12086, CVE-2024-12087, CVE-2024-12088, GHSA-p5pg-x43v-mvqj
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-01-15
Source: https://osv.dev/vulnerability/CVE-2024-12084
Type: osv

## Details
A heap-based buffer overflow flaw was found in the rsync daemon. This issue is due to improper handling of attacker-controlled checksum lengths (s2length) in the code. When MAX_DIGEST_LEN exceeds the fixed SUM_LENGTH (16 bytes), an attacker can write out of bounds in the sum2 buffer.

## References
- http://www.openwall.com/lists/oss-security/2025/01/14/6
- https://access.redhat.com/downloads/content/package-browser/
- https://kb.cert.org/vuls/id/952657
- https://www.kb.cert.org/vuls/id/952657
- https://access.redhat.com/errata/RHBA-2025:6470
- https://access.redhat.com/security/cve/CVE-2024-12084
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/12xxx/CVE-2024-12084.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-12084
- https://security.netapp.com/advisory/ntap-20250131-0002/
- https://bugzilla.redhat.com/show_bug.cgi?id=2330527
- https://github.com/RsyncProject/rsync
- https://github.com/google/security-research/security/advisories/GHSA-p5pg-x43v-mvqj
