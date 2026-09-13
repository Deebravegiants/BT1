# [M] CVE-2017-8891

## Summary
Severity: Medium
Advisory: CVE-2017-8891
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-05-10
Source: https://osv.dev/vulnerability/CVE-2017-8891
Type: osv

## Details
Dropbox Lepton 1.2.1 allows DoS (SEGV and application crash) via a malformed lepton file because the code does not ensure setup of a correct number of threads.

## References
- http://openwall.com/lists/oss-security/2017/05/10/1
- https://github.com/dropbox/lepton/commit/82167c144a322cc956da45407f6dce8d4303d346
- https://github.com/dropbox/lepton/issues/87
