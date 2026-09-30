# [M] Improper Privilege Management in transformeroptimus/superagi

## Summary
Severity: Medium
Advisory: CVE-2024-9431
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2025-03-20
Source: https://osv.dev/vulnerability/CVE-2024-9431
Type: osv

## Details
In version v0.0.14 of transformeroptimus/superagi, there is an improper privilege management vulnerability. After logging into the system, users can change the passwords of other users, leading to potential account takeover.

## References
- https://huntr.com/bounties/9b33d7c1-ed0a-4f5b-a378-694570fd990b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/9xxx/CVE-2024-9431.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-9431
