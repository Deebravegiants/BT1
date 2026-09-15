# [M] CVE-2023-46657

## Summary
Severity: Medium
Advisory: CVE-2023-46657
Aliases: GHSA-885r-hhpr-cc9p
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2023-10-25
Source: https://osv.dev/vulnerability/CVE-2023-46657
Type: osv

## Details
Jenkins Gogs Plugin 1.0.15 and earlier uses a non-constant time comparison function when checking whether the provided and expected webhook token are equal, potentially allowing attackers to use statistical methods to obtain a valid webhook token.

## References
- http://www.openwall.com/lists/oss-security/2023/10/25/2
- https://www.jenkins.io/security/advisory/2023-10-25/#SECURITY-2896
