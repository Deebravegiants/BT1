# [C] CVE-2017-15047

## Summary
Severity: Critical
Advisory: CVE-2017-15047
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-10-06
Source: https://osv.dev/vulnerability/CVE-2017-15047
Type: osv

## Details
The clusterLoadConfig function in cluster.c in Redis 4.0.2 allows attackers to cause a denial of service (out-of-bounds array index and application crash) or possibly have unspecified other impact by leveraging "limited access to the machine."

## References
- https://security.gentoo.org/glsa/202008-17
- https://github.com/antirez/redis/issues/4278
