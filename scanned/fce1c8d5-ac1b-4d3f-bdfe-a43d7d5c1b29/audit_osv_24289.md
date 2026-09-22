# [H] CVE-2023-0122

## Summary
Severity: High
Advisory: CVE-2023-0122
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-01-17
Source: https://osv.dev/vulnerability/CVE-2023-0122
Type: osv

## Details
A NULL pointer dereference vulnerability in the Linux kernel NVMe functionality, in nvmet_setup_auth(), allows an attacker to perform a Pre-Auth Denial of Service (DoS) attack on a remote machine. Affected versions v6.0-rc1 to v6.0-rc3, fixed in v6.0-rc4.

## References
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=da0342a3aa0357795224e6283df86444e1117168
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/0xxx/CVE-2023-0122.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-0122
- https://security.netapp.com/advisory/ntap-20230302-0002/
- http://www.openwall.com/lists/oss-security/2023/01/18/1
