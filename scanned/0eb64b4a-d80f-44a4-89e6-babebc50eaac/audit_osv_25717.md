# [M] Tcpreplay: tcprewrite: double free in tcpedit_dlt_cleanup() in plugins/dlt_plugins.c

## Summary
Severity: Medium
Advisory: CVE-2023-4256
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2023-12-21
Source: https://osv.dev/vulnerability/CVE-2023-4256
Type: osv

## Details
Within tcpreplay's tcprewrite, a double free vulnerability has been identified in the tcpedit_dlt_cleanup() function within plugins/dlt_plugins.c. This vulnerability can be exploited by supplying a specifically crafted file to the tcprewrite binary. This flaw enables a local attacker to initiate a Denial of Service (DoS) attack.

## References
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/EHUILQV2YJI5TXXXJA5FQ2HJQGFT7NTN/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/TMW5CIODKRHUUH7NTAYIRWGSJ56DTGXM/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/V3GYCHPVJ2VFN3D7FI4IRMDVMILLWBRF/
- https://packages.fedoraproject.org/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/4xxx/CVE-2023-4256.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-4256
- https://bugzilla.redhat.com/show_bug.cgi?id=2255212
- https://github.com/appneta/tcpreplay/issues/813
