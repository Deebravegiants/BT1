# [H] CVE-2022-0185

## Summary
Severity: High
Advisory: CVE-2022-0185
Aliases: A-213172369, PUB-A-213172369
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-02-11
Source: https://osv.dev/vulnerability/CVE-2022-0185
Type: osv

## Details
A heap-based buffer overflow flaw was found in the way the legacy_parse_param function in the Filesystem Context functionality of the Linux kernel verified the supplied parameters length. An unprivileged (in case of unprivileged user namespaces enabled, otherwise needs namespaced CAP_SYS_ADMIN privilege) local user able to open a filesystem that does not support the Filesystem Context API (and thus fallbacks to legacy handling) could use this flaw to escalate their privileges on the system.

## References
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2022-0185
- https://security.netapp.com/advisory/ntap-20220225-0003/
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=722d94847de2
- https://www.openwall.com/lists/oss-security/2022/01/18/7
- https://github.com/Crusaders-of-Rust/CVE-2022-0185
- https://www.willsroot.io/2022/01/cve-2022-0185.html
