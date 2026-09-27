# [M] CVE-2023-47268

## Summary
Severity: Medium
Advisory: CVE-2023-47268
CVSS: 5.3 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:L)
Published: 2026-05-08
Source: https://osv.dev/vulnerability/CVE-2023-47268
Type: osv

## Details
In libslic3r/GCode/PostProcessor.cpp in Prusa PrusaSlicer through 2.6.1, a crafted 3mf project file can execute arbitrary code on a host where the project is sliced and G-code exported.

## References
- https://help.prusa3d.com/article/post-processing-scripts_283913
- https://raw.githubusercontent.com/vulncheck-oss/0day.today.archive/main/local-exploits/39547.txt
- https://slic3r.org/download/
- https://www.prusa3d.com/page/prusaslicer_424/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/47xxx/CVE-2023-47268.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-47268
