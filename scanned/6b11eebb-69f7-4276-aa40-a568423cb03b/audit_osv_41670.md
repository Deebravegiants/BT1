# [M] ProFTPD mod_sftp Signed Integer Overflow via SCP Size-Record Parser

## Summary
Severity: Medium
Advisory: CVE-2026-63091
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-07-20
Source: https://osv.dev/vulnerability/CVE-2026-63091
Type: osv

## Details
ProFTPD before 1.3.9c and 1.3.10rc3 contains a signed integer overflow vulnerability in the mod_sftp module's SCP size-record parser that allows authenticated low-privilege attackers to bypass ASLR by sending a crafted file size value of UINT64_MAX, which results in a negative off_t value. Attackers can exploit the subsequent conversion to uint32_t, causing an approximately 4 GB requested read length and forcing the server to read beyond the end of the SSH channel data and write overread process memory into the uploaded file. In tested configurations, the disclosed data contains libc, libcrypto, and PIE pointers sufficient to derive their randomized base addresses, thereby bypassing ASLR and enabling reliable exploitation of memory corruption vulnerabilities in the same process.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63091.json
- https://github.com/proftpd/proftpd/blob/master/RELEASE_NOTES
- https://nvd.nist.gov/vuln/detail/CVE-2026-63091
- https://www.vulncheck.com/advisories/proftpd-mod-sftp-signed-integer-overflow-via-scp-size-record-parser
- https://github.com/proftpd/proftpd/commit/b9b7dde1bcd74bc23366484d53856b67b8d6d95e
- https://github.com/proftpd/proftpd/pull/2201
- https://github.com/proftpd/proftpd/releases/tag/v1.3.10rc3-3
- https://github.com/proftpd/proftpd/releases/tag/v1.3.9c
- https://github.com/proftpd/proftpd
