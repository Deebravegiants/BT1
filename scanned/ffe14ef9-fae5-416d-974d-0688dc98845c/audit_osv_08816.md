# [M] CVE-2016-6238

## Summary
Severity: Medium
Advisory: CVE-2016-6238
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-02-02
Source: https://osv.dev/vulnerability/CVE-2016-6238
Type: osv

## Details
The write_ujpg function in lepton/jpgcoder.cc in Dropbox lepton 1.0 allows remote attackers to cause denial of service (out-of-bounds read) via a crafted jpeg file.

## References
- http://www.openwall.com/lists/oss-security/2016/07/17/6
- https://github.com/dropbox/lepton/issues/26
