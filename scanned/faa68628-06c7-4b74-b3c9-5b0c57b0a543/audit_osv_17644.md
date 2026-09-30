# [H] CVE-2020-18428

## Summary
Severity: High
Advisory: CVE-2020-18428
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-07-26
Source: https://osv.dev/vulnerability/CVE-2020-18428
Type: osv

## Details
tinyexr commit 0.9.5 was discovered to contain an array index error in the tinyexr::SaveEXR component, which can lead to a denial of service (DOS).

## References
- https://github.com/syoyo/tinyexr/issues/109
- https://github.com/ChijinZ/security_advisories/tree/master/tinyexr_65f9859
