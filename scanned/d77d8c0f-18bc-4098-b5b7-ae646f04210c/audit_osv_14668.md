# [M] CVE-2019-10654

## Summary
Severity: Medium
Advisory: CVE-2019-10654
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-03-30
Source: https://osv.dev/vulnerability/CVE-2019-10654
Type: osv

## Details
The lzo1x_decompress function in liblzo2.so.2 in LZO 2.10, as used in Long Range Zip (aka lrzip) 0.631, allows remote attackers to cause a denial of service (invalid memory read and application crash) via a crafted archive, a different vulnerability than CVE-2017-8845.

## References
- https://github.com/ckolivas/lrzip/issues/108
