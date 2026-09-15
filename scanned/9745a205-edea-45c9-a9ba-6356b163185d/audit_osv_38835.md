# [C] CVE-2026-42484

## Summary
Severity: Critical
Advisory: CVE-2026-42484
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-01
Source: https://osv.dev/vulnerability/CVE-2026-42484
Type: osv

## Details
A heap-based buffer overflow in hex_to_binary in the PKZIP hash parser in hashcat v7.1.2 allows an attacker to cause a denial of service or possibly execute arbitrary code via a crafted PKZIP hash file. The issue affects modules 17200, 17210, 17220, 17225, and 17230. When data_type_enum<=1, attacker-controlled hex data from a user-supplied hash string is decoded into a fixed-size buffer without proper input-length validation.

## References
- https://gist.github.com/sgInnora/107f2eb20367e47d58c911e38d56a91f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/42xxx/CVE-2026-42484.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-42484
