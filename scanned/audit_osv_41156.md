# [M] libssh2 - Integer Overflow in publickey Subsystem Attribute Allocation

## Summary
Severity: Medium
Advisory: CVE-2026-58050
CVSS: 6.0 (CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:N/VC:L/VI:L/VA:H/SC:N/SI:N/SA:N)
Published: 2026-06-28
Source: https://osv.dev/vulnerability/CVE-2026-58050
Type: osv

## Details
libssh2 through 1.11.1 reads an attacker-controlled 32-bit attribute count from a publickey-subsystem response and uses it in the allocation num_attrs * sizeof(libssh2_publickey_attribute) without bounds checking, so on 32-bit platforms the multiplication overflows to an undersized buffer. A malicious SSH server can then drive the attribute-parsing loop to write past the allocation, causing a heap buffer overflow in a connecting libssh2 client.

## References
- https://github.com/libssh2/libssh2/blob/master/src/publickey.c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/58xxx/CVE-2026-58050.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-58050
- https://www.vulncheck.com/advisories/libssh2-integer-overflow-in-publickey-subsystem-attribute-allocation
- https://github.com/bikini/exploitarium/tree/main/libssh2-publickey-list-calc-poc
