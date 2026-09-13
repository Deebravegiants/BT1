# [H] CVE-2025-45768

## Summary
Severity: High
Advisory: CVE-2025-45768
Aliases: PYSEC-2025-183
CVSS: 7.0 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:H)
Published: 2025-07-31
Source: https://osv.dev/vulnerability/CVE-2025-45768
Type: osv

## Details
pyjwt v2.10.1 was discovered to contain weak encryption. NOTE: this is disputed by the Supplier because the key length is chosen by the application that uses the library (admittedly, library users may benefit from a minimum value and a mechanism for opting in to strict enforcement).

## References
- https://gist.github.com/ZupeiNie/6f65e564f2067b876321d3dfdbb76569
- https://github.com/jpadilla
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/45xxx/CVE-2025-45768.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-45768
- https://github.com/jpadilla/pyjwt
