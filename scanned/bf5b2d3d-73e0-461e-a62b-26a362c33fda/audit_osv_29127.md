# [H] xrdp allows an ininite number of login attempts

## Summary
Severity: High
Advisory: CVE-2024-39917
Aliases: GHSA-7w22-h4w7-8j5j
CVSS: 7.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:N/A:L)
Published: 2024-07-12
Source: https://osv.dev/vulnerability/CVE-2024-39917
Type: osv

## Details
xrdp is an open source RDP server. xrdp versions prior to 0.10.0 have a vulnerability that allows attackers to make an infinite number of login attempts. The number of max login attempts is supposed to be  limited by a configuration parameter `MaxLoginRetry` in `/etc/xrdp/sesman.ini`. However, this mechanism was not effectively working. As a result, xrdp allows an infinite number of login attempts.

## References
- https://lists.debian.org/debian-lts-announce/2025/05/msg00018.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/39xxx/CVE-2024-39917.json
- https://github.com/neutrinolabs/xrdp/security/advisories/GHSA-7w22-h4w7-8j5j
- https://nvd.nist.gov/vuln/detail/CVE-2024-39917
- https://github.com/neutrinolabs/xrdp/commit/19c111c74c913ecc6e4ba9a738ed929a79d2ae8f
