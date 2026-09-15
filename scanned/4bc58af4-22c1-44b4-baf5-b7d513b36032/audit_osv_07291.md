# [M] BIT-pillow-2020-35655

## Summary
Severity: Medium
Advisory: BIT-pillow-2020-35655
Aliases: CVE-2020-35655, GHSA-hf64-x4gq-p99h, PYSEC-2021-71
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-pillow-2020-35655
Type: osv

## Affected
- Bitnami: `pillow` — affected >=4.3.0 <8.1.0

## Details
In Pillow before 8.1.0, SGIRleDecode has a 4-byte buffer over-read when decoding crafted SGI RLE image files because offsets and length tables are mishandled.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/6BYVI5G44MRIPERKYDQEL3S3YQCZTVHE/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/BF553AMNNNBW7SH4IM4MNE4M6GNZQ7YD/
- https://pillow.readthedocs.io/en/stable/releasenotes/index.html
- https://nvd.nist.gov/vuln/detail/CVE-2020-35655
