# [M] CVE-2023-31518

## Summary
Severity: Medium
Advisory: CVE-2023-31518
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2023-05-23
Source: https://osv.dev/vulnerability/CVE-2023-31518
Type: osv

## Details
A heap use-after-free in the component CDataFileReader::GetItem of teeworlds v0.7.5 allows attackers to cause a Denial of Service (DoS) via a crafted map file.

## References
- https://gist.github.com/manba-bryant/9ca95d69c65f4d2c55946932c946fb9b
- https://mmmds.pl/fuzzing-map-parser-part-1-teeworlds/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/31xxx/CVE-2023-31518.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-31518
- https://github.com/teeworlds/teeworlds/issues/2970
