# [M] CVE-2022-43673

## Summary
Severity: Medium
Advisory: CVE-2022-43673
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-11-18
Source: https://osv.dev/vulnerability/CVE-2022-43673
Type: osv

## Details
Wire through 3.22.3993 on Windows advertises deletion of sent messages; nonetheless, all messages can be retrieved (for a limited period of time) from the AppData\Roaming\Wire\IndexedDB\https_app.wire.com_0.indexeddb.leveldb database.

## References
- https://wire.com/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/43xxx/CVE-2022-43673.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-43673
- https://www.secuvera.de/advisories/secuvera-SA-2022-01.txt
