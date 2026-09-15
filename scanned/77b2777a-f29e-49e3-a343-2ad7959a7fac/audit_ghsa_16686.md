# [C] CraftBeerPi 4 allows arbitrary code execution

## Summary
Severity: Critical
Advisory: GHSA-4f92-w438-f484
CVE: CVE-2024-3955
CWE: CWE-94
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-05-02
Source: https://github.com/advisories/GHSA-4f92-w438-f484
Type: github-advisory

## Affected
- PyPI: `cbpi4` — affected >=4.0.0.58 <4.4.1.a1

## Details
URL GET parameter "logtime" utilized within the "downloadlog" function from "cbpi/http_endpoints/http_system.py" is subsequently passed to the "os.system" function in "cbpi/controller/system_controller.py" without prior validation allowing arbitrary code execution. This issue affects CraftBeerPi 4: from 4.0.0.58 (commit 563fae9) before 4.4.1.a1 (commit 57572c7).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-3955
- https://github.com/PiBrewing/craftbeerpi4/issues/132
- https://cert.pl/en/posts/2024/05/CVE-2024-3955
- https://cert.pl/posts/2024/05/CVE-2024-3955
- https://github.com/PiBrewing/craftbeerpi4
