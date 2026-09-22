# [M] Eclipse Open J9 With -Xgc:concurrentScavenge on IBM Z, could write/read outside of a buffer

## Summary
Severity: Medium
Advisory: CVE-2024-3933
CVSS: 5.3 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:H/A:L)
Published: 2024-05-27
Source: https://osv.dev/vulnerability/CVE-2024-3933
Type: osv

## Details
In Eclipse OpenJ9 release versions prior to 0.44.0 and after 0.13.0, when running with JVM option -Xgc:concurrentScavenge, the sequence generated for System.arrayCopy on the IBM Z platform with hardware and software support for guarded storage [1], could allow access to a buffer with an incorrect length value when executing an arraycopy sequence while the Concurrent Scavenge Garbage Collection cycle is active and the source and destination memory regions for arraycopy overlap. This allows read and write to addresses beyond the end of the array range.

## References
- https://github.com/eclipse/omr/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/3xxx/CVE-2024-3933.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-3933
- https://gitlab.eclipse.org/security/cve-assignement/-/issues/21
- https://github.com/eclipse/omr/pull/7275
