# [M] Libkcapi: infinite loop denial of service in libkcapi _kcapi_aio_read_all() due to unhandled io_getevents() timeout return

## Summary
Severity: Medium
Advisory: CVE-2026-71227
CVSS: 5.1 (CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-05
Source: https://osv.dev/vulnerability/CVE-2026-71227
Type: osv

## Details
A flaw was found in libkcapi. A local attacker can influence an application that uses the Asynchronous Input/Output (AIO) interface. By reusing an AIO-enabled handle after a prior completion error, the _kcapi_aio_read_all() function can enter a non-terminating wait loop. This can lead to a persistent denial of service, making the affected application or thread unresponsive.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://catalog.redhat.com/software/containers/
- https://access.redhat.com/errata/RHSA-2026:56985
- https://access.redhat.com/security/cve/CVE-2026-71227
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/71xxx/CVE-2026-71227.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-71227
- https://bugzilla.redhat.com/show_bug.cgi?id=2462867
- https://github.com/smuellerDD/libkcapi
