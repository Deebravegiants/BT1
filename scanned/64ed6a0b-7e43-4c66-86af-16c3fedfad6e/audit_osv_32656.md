# [C] Fanwei E-Office Unauthenticated File Upload

## Summary
Severity: Critical
Advisory: CVE-2025-34046
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2025-06-26
Source: https://osv.dev/vulnerability/CVE-2025-34046
Type: osv

## Details
An unauthenticated file upload vulnerability exists in the Fanwei E-Office <= v9.4 web management interface. The vulnerability affects the /general/index/UploadFile.php endpoint, which improperly validates uploaded files when invoked with certain parameters (uploadType=eoffice_logo or uploadType=theme). An attacker can exploit this flaw by sending a crafted HTTP POST request to upload arbitrary files without requiring authentication. Successful exploitation could enable remote code execution on the affected server, leading to complete compromise of the web application and potentially the underlying system. Exploitation evidence was observed by the Shadowserver Foundation on 2025-02-05 UTC.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/34xxx/CVE-2025-34046.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-34046
- https://vulncheck.com/advisories/fanwei-eoffice-file-upload
- https://www.cnvd.org.cn/flaw/show/CNVD-2021-49104
- https://github.com/M0ge/CNVD-2021-49104-Fanwei-Eoffice-fileupload/blob/main/eoffice_fileupload.py
- https://github.com/projectdiscovery/nuclei-templates/blob/main/http/cnvd/2021/CNVD-2021-49104.yaml
