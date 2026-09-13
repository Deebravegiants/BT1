# [H] CVE-2020-6860

## Summary
Severity: High
Advisory: CVE-2020-6860
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2020-01-13
Source: https://osv.dev/vulnerability/CVE-2020-6860
Type: osv

## Details
libmysofa 0.9.1 has a stack-based buffer overflow in readDataVar in hdf/dataobject.c during the reading of a header message attribute.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/PGQ45S4RH7MC42NHTAGOIHYR4C5IRTMZ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/WGY7TAZX2M4NYXXGNHIBBKKN5XMSMKQ4/
- https://github.com/hoene/libmysofa/issues/96
