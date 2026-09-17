# [H] BIT-pillow-2020-35654

## Summary
Severity: High
Advisory: BIT-pillow-2020-35654
Aliases: CVE-2020-35654, GHSA-vqcj-wrf2-7v73, PYSEC-2021-70
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-pillow-2020-35654
Type: osv

## Affected
- Bitnami: `pillow` — affected >=0 <8.1.0

## Details
In Pillow before 8.1.0, TiffDecode has a heap-based buffer overflow when decoding crafted YCbCr files because of certain interpretation conflicts with LibTIFF in RGBA mode.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/6BYVI5G44MRIPERKYDQEL3S3YQCZTVHE/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/BF553AMNNNBW7SH4IM4MNE4M6GNZQ7YD/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/TQQY6472RX4J2SUJENWDZAWKTJJGP2ML/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ZTSY25UJU7NJUFHH3HWT575LT4TDFWBZ/
- https://pillow.readthedocs.io/en/stable/releasenotes/index.html
- https://nvd.nist.gov/vuln/detail/CVE-2020-35654
