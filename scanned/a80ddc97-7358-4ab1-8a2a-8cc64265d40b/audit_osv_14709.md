# [C] CVE-2019-10907

## Summary
Severity: Critical
Advisory: CVE-2019-10907
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-04-07
Source: https://osv.dev/vulnerability/CVE-2019-10907
Type: osv

## Details
Airsonic 10.2.1 uses Spring's default remember-me mechanism based on MD5, with a fixed key of airsonic in GlobalSecurityConfig.java. An attacker able to capture cookies might be able to trivially bruteforce offline the passwords of associated users.

## References
- https://github.com/airsonic/airsonic/commit/3e07ea52885f88d3fbec444dfd592f27bfb65647
