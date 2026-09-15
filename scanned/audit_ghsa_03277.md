# [H] Improper Input Validation in libseccomp-golang

## Summary
Severity: High
Advisory: GHSA-58v3-j75h-xr49
CVE: CVE-2017-18367
CWE: CWE-284
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2021-05-18
Source: https://github.com/advisories/GHSA-58v3-j75h-xr49
Type: github-advisory

## Affected
- Go: `github.com/seccomp/libseccomp-golang` — affected >=0 <0.9.1

## Details
libseccomp-golang 0.9.0 and earlier incorrectly generates BPFs that OR multiple arguments rather than ANDing them. A process running under a restrictive seccomp filter that specified multiple syscall arguments could bypass intended access restrictions by specifying a single matching argument.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-18367
- https://github.com/seccomp/libseccomp-golang/issues/22
- https://github.com/seccomp/libseccomp-golang/commit/06e7a29f36a34b8cf419aeb87b979ee508e58f9e
- https://access.redhat.com/errata/RHSA-2019:4087
- https://access.redhat.com/errata/RHSA-2019:4090
- https://lists.debian.org/debian-lts-announce/2020/08/msg00016.html
- https://usn.ubuntu.com/4574-1
- http://www.openwall.com/lists/oss-security/2019/04/25/6
