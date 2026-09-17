# [C] CVE-2019-10908

## Summary
Severity: Critical
Advisory: CVE-2019-10908
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-04-07
Source: https://osv.dev/vulnerability/CVE-2019-10908
Type: osv

## Details
In Airsonic 10.2.1, RecoverController.java generates passwords via org.apache.commons.lang.RandomStringUtils, which uses java.util.Random internally. This PRNG has a 48-bit seed that can easily be bruteforced, leading to trivial privilege escalation attacks.

## References
- https://github.com/airsonic/airsonic/commit/61c842923a6d60d4aedd126445a8437b53b752c8
