# [H] CVE-2018-20847

## Summary
Severity: High
Advisory: CVE-2018-20847
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-06-26
Source: https://osv.dev/vulnerability/CVE-2018-20847
Type: osv

## Details
An improper computation of p_tx0, p_tx1, p_ty0 and p_ty1 in the function opj_get_encoding_parameters in openjp2/pi.c in OpenJPEG through 2.3.0 can lead to an integer overflow.

## References
- http://www.securityfocus.com/bid/108921
- https://lists.debian.org/debian-lts-announce/2019/07/msg00010.html
- https://github.com/uclouvain/openjpeg/commit/5d00b719f4b93b1445e6fb4c766b9a9883c57949
- https://github.com/uclouvain/openjpeg/issues/431
- https://github.com/uclouvain/openjpeg/pull/1168/commits/c58df149900df862806d0e892859b41115875845
