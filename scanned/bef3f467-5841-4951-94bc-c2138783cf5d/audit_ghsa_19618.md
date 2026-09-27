# [H] Open WebUI has vulnerable dependency on starlette via fastapi

## Summary
Severity: High
Advisory: GHSA-w466-2wfc-8g58
CWE: CWE-400
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-03-20
Source: https://github.com/advisories/GHSA-w466-2wfc-8g58
Type: github-advisory

## Affected
- PyPI: `open-webui` — affected >=0

## Details
In version 0.3.32 of open-webui, the application uses a vulnerable version of the starlette package through its dependency on fastapi. The starlette package versions <=0.49 are susceptible to uncontrolled resource consumption, which can be exploited to cause a denial of service through memory exhaustion. This issue is addressed in fastapi version 0.115.3.

## References
- https://github.com/encode/starlette/security/advisories/GHSA-f96h-pmfr-66vw
- https://nvd.nist.gov/vuln/detail/CVE-2024-47874
- https://github.com/open-webui/open-webui
- https://huntr.com/bounties/56175583-70e3-4d53-94de-3f3a8e2423ec
