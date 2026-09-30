# [C] CVE-2019-11371

## Summary
Severity: Critical
Advisory: CVE-2019-11371
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-04-20
Source: https://osv.dev/vulnerability/CVE-2019-11371
Type: osv

## Details
BWA (aka Burrow-Wheeler Aligner) 0.7.17 r1198 has a Buffer Overflow via a long prefix that is mishandled in bns_fasta2bntseq and bns_dump at btnseq.c.

## References
- https://github.com/lh3/bwa/issues/239
