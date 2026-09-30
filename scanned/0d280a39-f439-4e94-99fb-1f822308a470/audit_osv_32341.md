# [M] Applio allows arbitrary file read in train.py export_pth function

## Summary
Severity: Medium
Advisory: CVE-2025-27784
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N/E:P)
Published: 2025-03-19
Source: https://osv.dev/vulnerability/CVE-2025-27784
Type: osv

## Details
Applio is a voice conversion tool. Versions 3.2.8-bugfix and prior are vulnerable to arbitrary file read in train.py's `export_pth` function. This issue may lead to reading arbitrary files on the Applio server. It can also be used in conjunction with blind server-side request forgery to read files from servers on the internal network that the Applio server has access to. As of time of publication, no known patches are available.

## References
- https://github.com/IAHispano/Applio/blob/29b4a00e4be209f9aac51cd9ccffcc632dfb2973/tabs/train/train.py#L267
- https://github.com/IAHispano/Applio/blob/29b4a00e4be209f9aac51cd9ccffcc632dfb2973/tabs/train/train.py#L801
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/27xxx/CVE-2025-27784.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-27784
- https://securitylab.github.com/advisories/GHSL-2024-341_GHSL-2024-353_Applio/
