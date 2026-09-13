# [M] undici vulnerable to Denial of Service via unbounded decompression of compressed responses

## Summary
Severity: Medium
Advisory: CVE-2026-84890
Aliases: GHSA-3xpg-4rpp-hhhm
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-09-04
Source: https://osv.dev/vulnerability/CVE-2026-84890
Type: osv

## Details
undici's decompress interceptor decompresses response bodies according to the untrusted Content-Encoding header. While the number of content-encoding layers is capped, the total decompressed output size is unbounded and there is no configuration option to limit it. A malicious or faulty upstream can therefore return a small compressed payload, a compression bomb, that expands to hundreds of megabytes or more in client memory, an asymmetric resource consumption that can exhaust memory and crash the process. This affects undici versions from 7.15.0 up to 7.29.1 and from 8.0.0 up to 8.10.2. Users should upgrade to undici 7.29.1 or 8.10.2.

## References
- https://cna.openjsf.org/security-advisories.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/84xxx/CVE-2026-84890.json
- https://github.com/nodejs/undici/security/advisories/GHSA-3xpg-4rpp-hhhm
- https://nvd.nist.gov/vuln/detail/CVE-2026-84890
