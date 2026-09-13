# [H] CVE-2026-42482

## Summary
Severity: High
Advisory: CVE-2026-42482
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-05-01
Source: https://osv.dev/vulnerability/CVE-2026-42482
Type: osv

## Details
A stack-based buffer overflow in mangle_to_hex_lower() and mangle_to_hex_upper() in src/rp_cpu.c in hashcat v7.1.2 allows an attacker to cause a denial of service or possibly execute arbitrary code via a crafted rule file, or via the -j or -k rule options used with password candidates of 128 or more characters. The vulnerability is caused by a bounds check that fails to account for the 2x expansion that occurs when password bytes are converted to hexadecimal.

## References
- https://gist.github.com/sgInnora/107f2eb20367e47d58c911e38d56a91f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/42xxx/CVE-2026-42482.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-42482
