# [M] Arbitrary File Overwrite

## Summary
Severity: Medium
Advisory: CVE-2024-25975
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2024-05-29
Source: https://osv.dev/vulnerability/CVE-2024-25975
Type: osv

## Details
The application implements an up- and downvote function which alters a value within a JSON file. The POST parameters are not filtered properly and therefore an arbitrary file can be overwritten. The file can be controlled by an authenticated attacker, the content cannot be controlled. It is possible to overwrite all files for which the webserver has write access. It is required to supply a relative path (path traversal).

## References
- http://seclists.org/fulldisclosure/2024/May/34
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/25xxx/CVE-2024-25975.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-25975
- https://r.sec-consult.com/hawki
- https://github.com/HAWK-Digital-Environments/HAWKI/commit/146967f3148e92d1640ffebc21d8914e2d7fb3f1
- https://github.com/HAWK-Digital-Environments/HAWKI
