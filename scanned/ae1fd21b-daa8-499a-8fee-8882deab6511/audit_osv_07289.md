# [H] BIT-pillow-2020-35653

## Summary
Severity: High
Advisory: BIT-pillow-2020-35653
Aliases: CVE-2020-35653, GHSA-f5g8-5qq7-938w, PYSEC-2021-69
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-pillow-2020-35653
Type: osv

## Affected
- Bitnami: `pillow` — affected >=0 <8.1.0

## Details
In Pillow before 8.1.0, PcxDecode has a buffer over-read when decoding a crafted PCX file because the user-supplied stride value is trusted for buffer calculations.

## References
- https://lists.debian.org/debian-lts-announce/2021/07/msg00018.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/6BYVI5G44MRIPERKYDQEL3S3YQCZTVHE/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/BF553AMNNNBW7SH4IM4MNE4M6GNZQ7YD/
- https://pillow.readthedocs.io/en/stable/releasenotes/index.html
- https://nvd.nist.gov/vuln/detail/CVE-2020-35653
