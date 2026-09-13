# [M] Stunnel: stack-based out-of-bounds read/write in stunnel s_vlog via oversized log message

## Summary
Severity: Medium
Advisory: CVE-2026-70368
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:L)
Published: 2026-08-04
Source: https://osv.dev/vulnerability/CVE-2026-70368
Type: osv

## Details
A stack-based out-of-bounds read vulnerability exists in the "s_vlog" function of stunnel, when handling oversized log messages via "vsnprintf". A remote attacker with network access to a stunnel service can send protocol inputs that trigger a log message longer than 1024 bytes, leading to an out-of-bounds stack read and a potential crash. In certain corner cases, the same vulnerability could be used to replace a series of trailing "\n" characters with "\0".

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://access.redhat.com/security/cve/CVE-2026-70368
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/70xxx/CVE-2026-70368.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-70368
- https://bugzilla.redhat.com/show_bug.cgi?id=2462029
- https://github.com/mtrojnar/stunnel
