# [M] Apache Answer: Using externally referenced images can leak user privacy.

## Summary
Severity: Medium
Advisory: CVE-2025-29868
Aliases: GHSA-wqcc-mfhw-53pc, GO-2025-3587
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2025-04-01
Source: https://osv.dev/vulnerability/CVE-2025-29868
Type: osv

## Details
Private Data Structure Returned From A Public Method vulnerability in Apache Answer.

This issue affects Apache Answer: through 1.4.2.

If a user uses an externally referenced image, when a user accesses this image, the provider of the image may obtain private information about the ip address of that accessing user.
Users are recommended to upgrade to version 1.4.5, which fixes the issue. In the new version, administrators can set whether external content can be displayed.

## References
- http://www.openwall.com/lists/oss-security/2025/04/01/2
- http://www.openwall.com/lists/oss-security/2025/04/02/1
- http://www.openwall.com/lists/oss-security/2025/04/10/3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/29xxx/CVE-2025-29868.json
- https://lists.apache.org/thread/l7pohw5g03g3qsvrz8pqc9t29mdv5lhf
- https://nvd.nist.gov/vuln/detail/CVE-2025-29868
