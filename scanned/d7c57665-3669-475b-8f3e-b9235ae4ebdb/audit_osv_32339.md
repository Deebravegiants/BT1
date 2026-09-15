# [M] Applio allows arbitrary file write in inference.py

## Summary
Severity: Medium
Advisory: CVE-2025-27782
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N/E:P)
Published: 2025-03-19
Source: https://osv.dev/vulnerability/CVE-2025-27782
Type: osv

## Details
Applio is a voice conversion tool. Versions 3.2.8-bugfix and prior are vulnerable to arbitrary file write in inference.py. This issue may lead to writing arbitrary files on the Applio server. It can also be used in conjunction with an unsafe deserialization to achieve remote code execution. As of time of publication, no known patches are available.

## References
- https://github.com/IAHispano/Applio/blob/d7d685fefd0c58e29e1d84d668613056791544a7/tabs/inference/inference.py#L1632-L1645
- https://github.com/IAHispano/Applio/blob/d7d685fefd0c58e29e1d84d668613056791544a7/tabs/inference/inference.py#L295
- https://github.com/IAHispano/Applio/blob/d7d685fefd0c58e29e1d84d668613056791544a7/tabs/inference/inference.py#L989-L1002
- https://github.com/IAHispano/Applio/blob/d7d685fefd0c58e29e1d84d668613056791544a7/tabs/tts/tts.py#L309-L322
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/27xxx/CVE-2025-27782.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-27782
- https://securitylab.github.com/advisories/GHSL-2024-341_GHSL-2024-353_Applio/
