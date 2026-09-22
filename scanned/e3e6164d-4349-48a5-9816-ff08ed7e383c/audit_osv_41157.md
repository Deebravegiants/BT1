# [M] libssh2 - Free of Uninitialized Pointer in publickey List Cleanup

## Summary
Severity: Medium
Advisory: CVE-2026-58051
CVSS: 6.0 (CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:N/VC:N/VI:L/VA:H/SC:N/SI:N/SA:N)
Published: 2026-06-28
Source: https://osv.dev/vulnerability/CVE-2026-58051
Type: osv

## Details
libssh2 through 1.11.1 grows its publickey list with SSH2_REALLOC but does not zero-initialize new entries before parsing populates them, so a parse failure reaching the cleanup path leaves libssh2_publickey_list_free operating on an uninitialized entry. A malicious SSH server offering the publickey subsystem can use a malformed response to make cleanup free an uninitialized, attacker-influenceable attrs pointer in a connecting libssh2 client.

## References
- https://github.com/libssh2/libssh2/blob/master/src/publickey.c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/58xxx/CVE-2026-58051.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-58051
- https://www.vulncheck.com/advisories/libssh2-free-of-uninitialized-pointer-in-publickey-list-cleanup
- https://github.com/bikini/exploitarium/tree/main/libssh2-publickey-list-calc-poc
