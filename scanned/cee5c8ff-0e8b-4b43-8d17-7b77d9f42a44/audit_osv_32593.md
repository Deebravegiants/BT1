# [M] Apache SeaTunnel: Unauthenticated insecure access

## Summary
Severity: Medium
Advisory: CVE-2025-32896
Aliases: GHSA-9x53-gr7p-4qf5
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2025-06-19
Source: https://osv.dev/vulnerability/CVE-2025-32896
Type: osv

## Details
# Summary

Unauthorized users can perform Arbitrary File Read and Deserialization
attack by submit job using restful api-v1.

# Details
Unauthorized users can access `/hazelcast/rest/maps/submit-job` to submit
job.
An attacker can set extra params in mysql url to perform Arbitrary File
Read and Deserialization attack.

This issue affects Apache SeaTunnel: <=2.3.10

# Fixed

Users are recommended to upgrade to version 2.3.11, and enable restful api-v2 & open https two-way authentication , which fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2025/04/12/1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/32xxx/CVE-2025-32896.json
- https://lists.apache.org/thread/qvh3zyt1jr25rgvw955rb8qjrnbxfro9
- https://nvd.nist.gov/vuln/detail/CVE-2025-32896
- https://github.com/apache/seatunnel/pull/9010
