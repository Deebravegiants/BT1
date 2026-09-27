# [M] openssl_encrypt before 1.4.9 Denial of Service via STREAMINFO

## Summary
Severity: Medium
Advisory: CVE-2026-81692
Aliases: GHSA-wr9q-p3rj-vqq7
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-27
Source: https://osv.dev/vulnerability/CVE-2026-81692
Type: osv

## Details
openssl_encrypt (pip: openssl-encrypt) versions 1.4.8 and earlier fail to validate the 36-bit STREAMINFO total_samples field of FLAC files before using it to size an allocation (np.random.randint(size=(total_samples, channels))). A ~50-byte crafted FLAC file declaring ~100 million samples causes a multi-gigabyte memory allocation, leading to out-of-memory denial of service during 'decrypt --stego-extract'. The issue is fixed in 1.4.9; both the 1.4.x and 1.5.x lines are affected.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/81xxx/CVE-2026-81692.json
- https://github.com/jahlives/openssl_encrypt/security/advisories/GHSA-wr9q-p3rj-vqq7
- https://nvd.nist.gov/vuln/detail/CVE-2026-81692
- https://www.vulncheck.com/advisories/openssl-encrypt-before-1.4.9-denial-of-service-via-streaminfo
