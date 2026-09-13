# [C] CVE-2017-1000458

## Summary
Severity: Critical
Advisory: CVE-2017-1000458
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-01-02
Source: https://osv.dev/vulnerability/CVE-2017-1000458
Type: osv

## Details
Bro before Bro v2.5.2 is vulnerable to an out of bounds write in the ContentLine analyzer allowing remote attackers to cause a denial of service (crash) and possibly other exploitation.

## References
- https://bro-tracker.atlassian.net/browse/BIT-1856
- https://github.com/bro/bro/commit/6c0f101a62489b1c5927b4ed63b0e1d37db40282
