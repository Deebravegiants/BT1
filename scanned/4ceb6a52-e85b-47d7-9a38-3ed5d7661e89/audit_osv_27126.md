# [M] Arbitrary File Read via Upload Function in binary-husky/gpt_academic

## Summary
Severity: Medium
Advisory: CVE-2024-10948
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2025-03-20
Source: https://osv.dev/vulnerability/CVE-2024-10948
Type: osv

## Details
A vulnerability in the upload function of binary-husky/gpt_academic allows any user to read arbitrary files on the system, including sensitive files such as `config.py`. This issue affects the latest version of the product. An attacker can exploit this vulnerability by intercepting the websocket request during file upload and replacing the file path with the path of the file they wish to read. The server then copies the file to the `private_upload` folder and provides the path to the copied file, which can be accessed via a GET request. This vulnerability can lead to the exposure of sensitive system files, potentially including credentials, configuration files, or sensitive user data.

## References
- https://huntr.com/bounties/290a379d-8441-4292-a553-3587e8c5c729
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/10xxx/CVE-2024-10948.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-10948
