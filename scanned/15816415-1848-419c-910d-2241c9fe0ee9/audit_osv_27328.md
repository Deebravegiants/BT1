# [H] Libdwarf: crashes randomly on fuzzed object

## Summary
Severity: High
Advisory: CVE-2024-2002
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-03-18
Source: https://osv.dev/vulnerability/CVE-2024-2002
Type: osv

## Details
A double-free vulnerability was found in libdwarf. In a multiply-corrupted DWARF object, libdwarf may try to dealloc(free) an allocation twice, potentially causing unpredictable and various results.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://github.com/davea42/libdwarf-code/
- https://github.com/davea42/libdwarf-code/blob/main/bugxml/data.txt
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/ZGPVLSPIXR32J6FOAFTTIMYTUUXJICGW/
- https://access.redhat.com/security/cve/CVE-2024-2002
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/2xxx/CVE-2024-2002.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-2002
- https://bugzilla.redhat.com/show_bug.cgi?id=2267700
