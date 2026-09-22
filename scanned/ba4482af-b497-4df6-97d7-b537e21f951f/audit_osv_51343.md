# [M] CVE-2021-28963

## Summary
Severity: Medium
Advisory: CVE-2021-28963
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2021-03-22
Source: https://osv.dev/vulnerability/CVE-2021-28963
Type: osv

## Details
Shibboleth Service Provider before 3.2.1 allows content injection because template generation uses attacker-controlled parameters.

## References
- https://git.shibboleth.net/view/?p=cpp-sp.git%3Ba=commit%3Bh=d1dbebfadc1bdb824fea63843c4c38fa69e54379
- https://www.debian.org/security/2021/dsa-4872
- https://bugs.debian.org/985405
- https://shibboleth.net/community/advisories/secadv_20210317.txt
- https://issues.shibboleth.net/jira/browse/SSPCPP-922
