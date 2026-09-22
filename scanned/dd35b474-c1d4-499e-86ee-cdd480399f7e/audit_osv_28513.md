# [M] CVE-2024-33901

## Summary
Severity: Medium
Advisory: CVE-2024-33901
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-05-20
Source: https://osv.dev/vulnerability/CVE-2024-33901
Type: osv

## Details
Issue in KeePassXC 2.7.7 allows an attacker (who has the privileges of the victim) to recover some passwords stored in the .kdbx database via a memory dump. NOTE: the vendor disputes this because memory-management constraints make this unavoidable in the current design and other realistic designs.

## References
- https://gist.github.com/Fastor01/30c6d89c842feb1865ec2cd2d3806838
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/33xxx/CVE-2024-33901.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-33901
- https://github.com/keepassxreboot/keepassxc/issues/10784
- https://keepassxc.org/blog/
- https://keepassxc.org/blog/2019-02-21-memory-security/
