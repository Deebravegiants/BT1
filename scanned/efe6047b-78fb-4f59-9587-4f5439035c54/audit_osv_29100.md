# [C] fishaudio/Bert-VITS2 Command Injection in webui_preprocess.py resample function

## Summary
Severity: Critical
Advisory: CVE-2024-39685
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-07-22
Source: https://osv.dev/vulnerability/CVE-2024-39685
Type: osv

## Details
Bert-VITS2 is the VITS2 Backbone with multilingual bert. User input supplied to the data_dir variable is used directly in a command executed with subprocess.run(cmd, shell=True) in the resample function, which leads to arbitrary command execution. This affects fishaudio/Bert-VITS2 2.3 and earlier.

## References
- https://github.com/fishaudio/Bert-VITS2/blob/3f8c537f4aeb281df3fb3c455eed9a1b64871a81/webui_preprocess.py#L46-L52
- https://github.com/fishaudio/Bert-VITS2/blob/76653b5b6d657143721df2ed6c5c246b4b1d9277/webui_preprocess.py#L130-L133
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/39xxx/CVE-2024-39685.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-39685
- https://securitylab.github.com/advisories/GHSL-2024-045_GHSL-2024-047_fishaudio_Bert-VITS2/
