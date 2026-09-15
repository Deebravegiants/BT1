# [M] c-ares out of bounds read in ares__read_line()

## Summary
Severity: Medium
Advisory: CVE-2024-25629
Aliases: GHSA-mg26-v6qh-x48q
CVSS: 4.4 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-02-23
Source: https://osv.dev/vulnerability/CVE-2024-25629
Type: osv

## Details
c-ares is a C library for asynchronous DNS requests. `ares__read_line()` is used to parse local configuration files such as `/etc/resolv.conf`, `/etc/nsswitch.conf`, the `HOSTALIASES` file, and if using a c-ares version prior to 1.27.0, the `/etc/hosts` file. If any of these configuration files has an embedded `NULL` character as the first character in a new line, it can lead to attempting to read memory prior to the start of the given buffer which may result in a crash. This issue is fixed in c-ares 1.27.0. No known workarounds exist.

## References
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/2P76QYINQNPEHUTEEDOUYIRZ2X6UVZ5K/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/CSCMTSPDIE2UHU34TIXQQHZ6JTE3Y3VF/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/GX37LFPFQ3T6FFMMFYQTEGIQXXN7F27U/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/25xxx/CVE-2024-25629.json
- https://github.com/c-ares/c-ares/security/advisories/GHSA-mg26-v6qh-x48q
- https://nvd.nist.gov/vuln/detail/CVE-2024-25629
- https://github.com/c-ares/c-ares/commit/a804c04ddc8245fc8adf0e92368709639125e183
