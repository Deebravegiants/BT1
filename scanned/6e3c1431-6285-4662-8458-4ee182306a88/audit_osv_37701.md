# [M] NetBSD Signed Integer Overflow in cryptodev_op via cryptodev.c

## Summary
Severity: Medium
Advisory: CVE-2026-32849
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:P/PR:L/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-05-18
Source: https://osv.dev/vulnerability/CVE-2026-32849
Type: osv

## Details
NetBSD prior to commit ec8451e contains a signed integer overflow vulnerability in the cryptodev_op() function in sys/opencrypto/cryptodev.c where the local variable iov_len is declared as a signed int but assigned from an unsigned cop->dst_len value, causing undefined behavior when cop->dst_len exceeds INT_MAX. A local attacker with access to /dev/crypto and a compression session type can exploit this vulnerability by providing a dst_len value exceeding INT_MAX to trigger a kernel panic through NULL pointer dereference when CONFIG_SVS is disabled and corrupted UIO pointer arithmetic.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/32xxx/CVE-2026-32849.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-32849
- https://www.vulncheck.com/advisories/netbsd-signed-integer-overflow-in-cryptodev-op-via-cryptodev-c
- https://github.com/NetBSD/src/commit/ec8451efc1565516aba9e7047e1a1a1ce7953a2f
- https://github.com/NetBSD/src
- https://nasm.re/posts/uaf_netbsd_crypto/
