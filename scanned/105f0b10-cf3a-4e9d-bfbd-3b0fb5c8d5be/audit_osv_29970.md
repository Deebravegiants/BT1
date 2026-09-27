# [H] CVE-2024-48077

## Summary
Severity: High
Advisory: CVE-2024-48077
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-01-15
Source: https://osv.dev/vulnerability/CVE-2024-48077
Type: osv

## Details
NanoMQ v0.22.7 is vulnerable to Denial of Service (DoS) due to improper resource throttling. A crafted sequence of requests causes the recv-q queue to saturate, leading to the rapid exhaustion of system file descriptors (FDs). This exhaustion triggers a process crash, rendering the broker unable to provide services.

## References
- https://gist.github.com/pengwGit/2379e7a8fe75d09621f7c060db0237c4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/48xxx/CVE-2024-48077.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-48077
- https://github.com/nanomq/nanomq
