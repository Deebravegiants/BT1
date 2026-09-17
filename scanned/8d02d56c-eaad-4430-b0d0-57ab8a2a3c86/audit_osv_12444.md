# [M] CVE-2018-12066

## Summary
Severity: Medium
Advisory: CVE-2018-12066
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-06-08
Source: https://osv.dev/vulnerability/CVE-2018-12066
Type: osv

## Details
BIRD Internet Routing Daemon before 1.6.4 allows local users to cause a denial of service (stack consumption and daemon crash) via BGP mask expressions in birdc.

## References
- http://bird.network.cz
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=900967
- https://gitlab.labs.nic.cz/labs/bird/blob/v1.6.4/NEWS#L11
- https://gitlab.labs.nic.cz/labs/bird/commit/e8bc64e308586b6502090da2775af84cd760ed0d
