# [M] Exim Regex use after free

## Summary
Severity: Medium
Advisory: CVE-2022-3559
CVSS: 4.6 (CVSS:3.1/AV:A/AC:H/PR:L/UI:N/S:U/C:L/I:L/A:L)
Published: 2022-10-17
Source: https://osv.dev/vulnerability/CVE-2022-3559
Type: osv

## Details
A vulnerability was found in Exim and classified as problematic. This issue affects some unknown processing of the component Regex Handler. The manipulation leads to use after free. The name of the patch is 4e9ed49f8f12eb331b29bd5b6dc3693c520fddc2. It is recommended to apply a patch to fix this issue. The identifier VDB-211073 was assigned to this vulnerability.

## References
- https://bugs.exim.org/show_bug.cgi?id=2915
- https://git.exim.org/exim.git/commit/4e9ed49f8f12eb331b29bd5b6dc3693c520fddc2
- https://lists.debian.org/debian-lts-announce/2024/10/msg00029.html
- https://vuldb.com/?id.211073
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/3xxx/CVE-2022-3559.json
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/EIH4W5R7SHTUEQFWWKB4TUO5YFZX64KV/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/TMQ6OCKPNPBPSD37YR4FOWV2R54M2UEP/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/WFHLZVHNNO2GWYP5EA4TZQZ5O4GVPARR/
- https://nvd.nist.gov/vuln/detail/CVE-2022-3559
