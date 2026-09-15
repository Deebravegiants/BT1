# [M] BIT-pillow-2020-10378

## Summary
Severity: Medium
Advisory: BIT-pillow-2020-10378
Aliases: CVE-2020-10378, GHSA-3xv8-3j54-hgrp, PYSEC-2020-77
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-pillow-2020-10378
Type: osv

## Affected
- Bitnami: `pillow` — affected >=0 <7.1.0

## Details
In libImaging/PcxDecode.c in Pillow before 7.1.0, an out-of-bounds read can occur when reading PCX files where state->shuffle is instructed to read beyond state->buffer.

## References
- https://github.com/python-pillow/Pillow/commit/6a83e4324738bb0452fbe8074a995b1c73f08de7#diff-9478f2787e3ae9668a15123b165c23ac
- https://github.com/python-pillow/Pillow/commits/master/src/libImaging
- https://github.com/python-pillow/Pillow/pull/4538
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/BEBCPE4F2VHTIT6EZA2YZQZLPVDEBJGD/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/HOKHNWV2VS5GESY7IBD237E7C6T3I427/
- https://pillow.readthedocs.io/en/stable/releasenotes/7.1.0.html
- https://usn.ubuntu.com/4430-1/
- https://usn.ubuntu.com/4430-2/
- https://nvd.nist.gov/vuln/detail/CVE-2020-10378
