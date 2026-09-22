# [M] eGovFramework <= 4.3.1 Unauthenticated Encryption Oracle via Web Editor Image Upload Endpoints

## Summary
Severity: Medium
Advisory: CVE-2025-34337
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2025-11-19
Source: https://osv.dev/vulnerability/CVE-2025-34337
Type: osv

## Details
eGovFramework/egovframe-common-components versions up to and including 4.3.1 includes Web Editor image upload and related file delivery functionality that uses symmetric encryption to protect URL parameters, but exposes an encryption oracle that allows attackers to generate valid ciphertext for chosen values. The image upload endpoints /utl/wed/insertImage.do and /utl/wed/insertImageCk.do encrypt server-side paths, filenames, and MIME types and embed them directly into a download URL that is returned to the client. Because these same encrypted parameters are trusted by other endpoints, such as /utl/web/imageSrc.do and /cmm/fms/getImage.do, an unauthenticated attacker can abuse the upload functionality to obtain encrypted representations of attacker-chosen identifiers and then replay those ciphertext values to file-serving APIs. This design failure allows an attacker to bypass access controls that rely solely on the secrecy of encrypted parameters and retrieve arbitrary stored files that are otherwise expected to require an existing session or specific authorization context. KISA/KrCERT has identified this unpatched vulnerability as "KVE-2023-5281."

## References
- https://www.egovframe.go.kr/eng/sub.do?menuNo=2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/34xxx/CVE-2025-34337.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-34337
- https://www.vulncheck.com/advisories/egovframework-unauthenticated-encryption-oracle-via-web-editor-image-upload-endpoints
- https://github.com/eGovFramework/egovframe-common-components
- https://pierrekim.github.io/advisories/2025-egovframe.txt
- https://pierrekim.github.io/blog/2025-11-20-egovframe-2-vulnerabilities.html
