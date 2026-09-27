# [M] WeiPHP Path Traversal Arbitrary File Read

## Summary
Severity: Medium
Advisory: CVE-2025-34045
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2025-06-26
Source: https://osv.dev/vulnerability/CVE-2025-34045
Type: osv

## Details
A path traversal vulnerability exists in WeiPHP 5.0, an open source WeChat public account platform development framework by Shenzhen Yuanmengyun Technology Co., Ltd. The flaw occurs in the picUrl parameter of the /public/index.php/material/Material/_download_imgage endpoint, where insufficient input validation allows unauthenticated remote attackers to perform directory traversal via crafted POST requests. This enables arbitrary file read on the server, potentially exposing sensitive information such as configuration files and source code. Exploitation evidence was observed by the Shadowserver Foundation on 2025-02-05 UTC.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/34xxx/CVE-2025-34045.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-34045
- https://vulncheck.com/advisories/weiphp-path-traversal-file-read
- https://www.cnvd.org.cn/flaw/show/CNVD-2020-68596
- https://github.com/projectdiscovery/nuclei-templates/blob/main/http/cnvd/2020/CNVD-2020-68596.yaml
