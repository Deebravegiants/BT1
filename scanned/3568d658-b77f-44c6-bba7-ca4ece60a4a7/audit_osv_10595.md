# [M] CVE-2017-17554

## Summary
Severity: Medium
Advisory: CVE-2017-17554
Aliases: GHSA-45h5-cqqw-9rjw, PYSEC-2017-76
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-12-12
Source: https://osv.dev/vulnerability/CVE-2017-17554
Type: osv

## Details
A NULL pointer dereference (DoS) Vulnerability was found in the function aubio_source_avcodec_readframe in io/source_avcodec.c of aubio 0.4.6, which may lead to DoS when playing a crafted audio file.

## References
- https://github.com/IvanCql/vulnerability/blob/master/An%20NULL%20pointer%20dereference%28DoS%29%20Vulnerability%20was%20found%20in%20function%20%20aubio_source_avcodec_readframe%20of%20aubio.md
