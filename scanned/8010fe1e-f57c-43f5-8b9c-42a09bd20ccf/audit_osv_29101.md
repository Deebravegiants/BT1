# [M] fishaudio/Bert-VITS2 Limited File Write in webui_preprocess.py generate_config function

## Summary
Severity: Medium
Advisory: CVE-2024-39688
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2024-07-22
Source: https://osv.dev/vulnerability/CVE-2024-39688
Type: osv

## Details
Bert-VITS2 is the VITS2 Backbone with multilingual bert. User input supplied to the data_dir variable is concatenated with other folders and used to open a new file in the generate_config function, which leads to a limited file write. The issue allows for writing /config/config.json file in arbitrary directory on the server. If a given directory path doesn’t exist, the application will return an error, so this vulnerability could also be used to gain information about existing directories on the server. This affects fishaudio/Bert-VITS2 2.3 and earlier.

## References
- https://github.com/fishaudio/Bert-VITS2/blob/76653b5b6d657143721df2ed6c5c246b4b1d9277/webui_preprocess.py#L130-L133
- https://github.com/fishaudio/Bert-VITS2/blob/76653b5b6d657143721df2ed6c5c246b4b1d9277/webui_preprocess.py#L34
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/39xxx/CVE-2024-39688.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-39688
- https://securitylab.github.com/advisories/GHSL-2024-045_GHSL-2024-047_fishaudio_Bert-VITS2/
