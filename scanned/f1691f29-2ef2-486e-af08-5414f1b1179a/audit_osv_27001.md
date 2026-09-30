# [M] Denial-of-Service in Gvisor

## Summary
Severity: Medium
Advisory: CVE-2023-7258
CVSS: 4.8 (CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:U/C:N/I:N/A:H)
Published: 2024-05-15
Source: https://osv.dev/vulnerability/CVE-2023-7258
Type: osv

## Details
A denial of service exists in Gvisor Sandbox where a bug in reference counting code in mount point tracking could lead to a panic, making it possible for an attacker running as root and with permission to mount volumes to kill the sandbox. We recommend upgrading past commit 6a112c60a257dadac59962e0bc9e9b5aee70b5b6

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/7xxx/CVE-2023-7258.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-7258
- https://github.com/google/gvisor/commit/6a112c60a257dadac59962e0bc9e9b5aee70b5b6
- https://github.com/google/gvisor
