# [H] Gin-vue-admin has arbitrary file upload vulnerability caused by path traversal

## Summary
Severity: High
Advisory: GHSA-3558-j79f-vvm6
CVE: CVE-2026-22786
CWE: CWE-22, CWE-434
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2026-01-13
Source: https://github.com/advisories/GHSA-3558-j79f-vvm6
Type: github-advisory

## Affected
- Go: `github.com/flipped-aurora/gin-vue-admin` — affected >=0

## Details
### Impact
Gin-vue-admin <= v2.8.7 has a path traversal vulnerability in the breakpoint resume upload functionality. Attacker can upload any files on any directory.

Path traversal vulnerabilities occur when a web application accepts user-supplied file paths without proper validation, allowing attackers to access or write files outside the intended directory. In the breakpoint_continue.go file, the MakeFile function accepts a fileName parameter through the /fileUploadAndDownload/breakpointContinueFinish API endpoint and directly concatenates it with the base directory path (./fileDir/) using os.OpenFile() without any validation for directory traversal sequences (e.g., ../).

Notably, while the related makeFileContent function in the same file properly validates the fileName parameter by checking for .. sequences, the MakeFile function lacks this security control, indicating an inconsistent security implementation.

An **attacker with file upload privileges (role ID 888 - super administrator)** could exploit this vulnerability by:

First uploading file chunks through the /fileUploadAndDownload/breakpointContinue endpoint (which has proper validation)

Then calling the /fileUploadAndDownload/breakpointContinueFinish endpoint with a malicious fileName parameter containing path traversal sequences (e.g., ../../../tmp/malicious.txt)

This could lead to:
Arbitrary file creation, application process, Configuration file overwriting, Potential Remote Code Execution......

### POC
1. Use this endpoint to upload any files(include *name or *file types)
<img width="1429" height="788" alt="Clipboard_Screenshot_1767755216" src="https://github.com/user-attachments/assets/516022d6-32af-4810-abd9-945cb0bc5ae5" />

2. Then, the `filename` parameter here uses `../` to traverse to an arbitrary path. 
<img width="1445" height="306" alt="Clipboard_Screenshot_1767755256" src="https://github.com/user-attachments/assets/577aa1c1-9b26-4082-b431-f9dac1cdc307" />

3. Proof
<img width="837" height="843" alt="Clipboard_Screenshot_1767755312" src="https://github.com/user-attachments/assets/66f51049-8dc8-4c94-994e-a6d8bc1196a9" />


### Patches
Please wait for the latest patch

## References
- https://github.com/flipped-aurora/gin-vue-admin/security/advisories/GHSA-3558-j79f-vvm6
- https://nvd.nist.gov/vuln/detail/CVE-2026-22786
- https://github.com/flipped-aurora/gin-vue-admin/commit/2242f5d6e133e96d1b359ac019bf54fa0e975dd5
- https://github.com/flipped-aurora/gin-vue-admin
