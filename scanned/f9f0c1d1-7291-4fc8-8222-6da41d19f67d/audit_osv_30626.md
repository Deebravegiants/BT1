# [M] CVE-2024-53384

## Summary
Severity: Medium
Advisory: CVE-2024-53384
Aliases: GHSA-3mv9-4h5g-vhg3
CVSS: 5.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2025-03-03
Source: https://osv.dev/vulnerability/CVE-2024-53384
Type: osv

## Details
A DOM Clobbering vulnerability in tsup v8.3.4 allows attackers to execute arbitrary code via a crafted script in the import.meta.url to document.currentScript in cjs_shims.js components

## References
- https://gist.github.com/jackfromeast/36f98bf7542d11835c883c1d175d9b92
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/53xxx/CVE-2024-53384.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-53384
