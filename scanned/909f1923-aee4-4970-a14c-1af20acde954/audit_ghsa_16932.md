# [M] PsiTransfer: File integrity violation

## Summary
Severity: Medium
Advisory: GHSA-2p2x-p7wj-j5h2
CVE: CVE-2024-31454
CWE: CWE-434
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2024-04-05
Source: https://github.com/advisories/GHSA-2p2x-p7wj-j5h2
Type: github-advisory

## Affected
- npm: `psitransfer` — affected >=0 <2.2.0

## Details
### Summary
The absence of restrictions on the endpoint, which is designed for uploading files, allows an attacker who received the id of a file distribution to change the files that are in this distribution.

### Details
Vulnerable endpoint: PATCH /files/{{id}}

### PoC
1. Create a file distribution.

2. Go to the link address for downloading files and download the file (in this case, the attacker receives the file id from the download request).

3. Send a PATCH /files/{{id}} request with arbitrary content in the request body.

Thus, the file with the specified id will be changed. What the attacker specifies in the body of the request will be added to the end of the original content. In the future, users will download the modified file.

### Impact
The vulnerability allows an attacker to influence those users who come to the file distribution after him and slip the victim files with a malicious or phishing signature.

## References
- https://github.com/psi-4ward/psitransfer/security/advisories/GHSA-2p2x-p7wj-j5h2
- https://nvd.nist.gov/vuln/detail/CVE-2024-31454
- https://github.com/psi-4ward/psitransfer/commit/0014d81141e0f1664ccb6841970ef1ea0237cca3
- https://github.com/psi-4ward/psitransfer
