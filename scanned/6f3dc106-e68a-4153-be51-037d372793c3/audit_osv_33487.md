# [C] GHSL-2025-012_Retrieval-based-Voice-Conversion-WebUI

## Summary
Severity: Critical
Advisory: CVE-2025-43842
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:P)
Published: 2025-05-05
Source: https://osv.dev/vulnerability/CVE-2025-43842
Type: osv

## Details
Retrieval-based-Voice-Conversion-WebUI is a voice changing framework based on VITS. Versions 2.2.231006 and prior are vulnerable to command injection. The variables exp_dir1, np7, trainset_dir4 and sr2 take user input and pass it to the preprocess_dataset function, which concatenates them into a command that is run on the server. This can lead to arbitrary command execution. As of time of publication, no known patches exist.

## References
- https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI/blob/7ef19867780cf703841ebafb565a4e47d1ea86ff/infer-web.py#L1227-L1232
- https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI/blob/7ef19867780cf703841ebafb565a4e47d1ea86ff/infer-web.py#L223-L232
- https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI/blob/7ef19867780cf703841ebafb565a4e47d1ea86ff/infer-web.py#L235
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/43xxx/CVE-2025-43842.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-43842
- https://securitylab.github.com/advisories/GHSL-2025-012_GHSL-2025-022_Retrieval-based-Voice-Conversion-WebUI/
