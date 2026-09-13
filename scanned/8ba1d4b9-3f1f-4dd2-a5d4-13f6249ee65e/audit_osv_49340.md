# [C] CVE-2019-10269

## Summary
Severity: Critical
Advisory: CVE-2019-10269
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-03-29
Source: https://osv.dev/vulnerability/CVE-2019-10269
Type: osv

## Details
BWA (aka Burrow-Wheeler Aligner) before 2019-01-23 has a stack-based buffer overflow in the bns_restore function in bntseq.c via a long sequence name in a .alt file.

## References
- https://usn.ubuntu.com/4087-1/
- https://github.com/lh3/bwa/pull/232
- https://coreymhudson.github.io/bwa_vulnerabilties/
