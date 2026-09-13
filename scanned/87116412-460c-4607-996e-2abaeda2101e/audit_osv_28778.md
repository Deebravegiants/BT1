# [H] CVE-2024-36474

## Summary
Severity: High
Advisory: CVE-2024-36474
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-10-03
Source: https://osv.dev/vulnerability/CVE-2024-36474
Type: osv

## Details
An integer overflow vulnerability exists in the Compound Document Binary File format parser of the GNOME Project G Structured File Library (libgsf) version v1.14.52. A specially crafted file can result in an integer overflow when processing the directory from the file that allows for an out-of-bounds index to be used when reading and writing to an array. This can lead to arbitrary code execution. An attacker can provide a malicious file to trigger this vulnerability.

## References
- https://lists.debian.org/debian-lts-announce/2024/10/msg00002.html
- https://talosintelligence.com/vulnerability_reports/TALOS-2024-2068
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2024-2068
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/36xxx/CVE-2024-36474.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-36474
- https://gitlab.gnome.org/GNOME/libgsf/-/issues/34
