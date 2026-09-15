# [M] Libvirt: stack use-after-free in virnetclientioeventloop()

## Summary
Severity: Medium
Advisory: CVE-2024-4418
CVSS: 6.2 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-08
Source: https://osv.dev/vulnerability/CVE-2024-4418
Type: osv

## Details
A race condition leading to a stack use-after-free flaw was found in libvirt. Due to a bad assumption in the virNetClientIOEventLoop() method, the `data` pointer to a stack-allocated virNetClientIOEventData structure ended up being used in the virNetClientIOEventFD callback while the data pointer's stack frame was concurrently being "freed" when returning from virNetClientIOEventLoop(). The 'virtproxyd' daemon can be used to trigger requests. If libvirt is configured with fine-grained access control, this issue, in theory, allows a user to escape their otherwise limited access. This flaw allows a local, unprivileged user to access virtproxyd without authenticating. Remote users would need to authenticate before they could access it.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/4IE44UIIC3QWBFRB4EUSFNLJBU6JLNSD/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/Q4ZQBAJVHIZMCZNTRPUW3ZKXRKLXRQZU/
- https://access.redhat.com/errata/RHSA-2024:4351
- https://access.redhat.com/errata/RHSA-2024:4432
- https://access.redhat.com/errata/RHSA-2024:4757
- https://access.redhat.com/security/cve/CVE-2024-4418
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/4xxx/CVE-2024-4418.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-4418
- https://security.netapp.com/advisory/ntap-20250411-0002/
- https://bugzilla.redhat.com/show_bug.cgi?id=2278616
- https://gitlab.com/libvirt/libvirt
