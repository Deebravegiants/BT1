# [M] Freeipa: specially crafted http requests potentially lead to denial of service

## Summary
Severity: Medium
Advisory: CVE-2024-1481
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2024-04-10
Source: https://osv.dev/vulnerability/CVE-2024-1481
Type: osv

## Details
A flaw was found in FreeIPA. This issue may allow a remote attacker to craft a HTTP request with parameters that can be interpreted as command arguments to kinit on the FreeIPA server, which can lead to a denial of service.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://github.com/freeipa/freeipa/
- https://lists.debian.org/debian-lts-announce/2024/03/msg00026.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/FKTET3PAOMCHBXUUY37X556PVA3DFQES/
- https://access.redhat.com/errata/RHSA-2024:2147
- https://access.redhat.com/errata/RHSA-2024:3044
- https://access.redhat.com/security/cve/CVE-2024-1481
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/1xxx/CVE-2024-1481.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-1481
- https://bugzilla.redhat.com/show_bug.cgi?id=2262169
