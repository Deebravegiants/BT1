# [M] CVE-2018-20820

## Summary
Severity: Medium
Advisory: CVE-2018-20820
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-04-23
Source: https://osv.dev/vulnerability/CVE-2018-20820
Type: osv

## Details
read_ujpg in jpgcoder.cc in Dropbox Lepton 1.2.1 allows attackers to cause a denial-of-service (application runtime crash because of an integer overflow) via a crafted file.

## References
- https://github.com/dropbox/lepton/commit/6a5ceefac1162783fffd9506a3de39c85c725761
- https://github.com/dropbox/lepton/issues/111
