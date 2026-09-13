# [H] CVE-2026-78136

## Summary
Severity: High
Advisory: CVE-2026-78136
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-08-23
Source: https://osv.dev/vulnerability/CVE-2026-78136
Type: osv

## Details
chirpmyradio CHIRP before 39178db allows eval injection via crafted CSV data. This occurs in _clean_tmode in drivers/kenwood_itm.py.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/78xxx/CVE-2026-78136.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-78136
- https://github.com/kk7ds/chirp/commit/39178dbfc4fece083ab9ed20286d6ae3a91a718e
- https://github.com/cduram/CHIRP-CodeExecution_via_Malicious_ImageFile
