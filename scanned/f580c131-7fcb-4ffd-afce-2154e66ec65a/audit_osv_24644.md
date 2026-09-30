# [M] CVE-2023-24619

## Summary
Severity: Medium
Advisory: CVE-2023-24619
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-02-13
Source: https://osv.dev/vulnerability/CVE-2023-24619
Type: osv

## Details
Redpanda before 22.3.12 discloses cleartext AWS credentials. The import functionality in the rpk binary logs an AWS Access Key ID and Secret in cleartext to standard output, allowing a local user to view the key in the console, or in Kubernetes logs if stdout output is collected. The fixed versions are 22.3.12, 22.2.10, and 22.1.12.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/24xxx/CVE-2023-24619.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-24619
- https://github.com/redpanda-data/redpanda/pull/8339
