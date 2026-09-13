# [H] baserCMS has Unsafe File Upload Leading to Remote Code Execution (RCE)

## Summary
Severity: High
Advisory: GHSA-hv78-cwp4-8r7r
CVE: CVE-2025-32957
CWE: CWE-434
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2026-03-31
Source: https://github.com/advisories/GHSA-hv78-cwp4-8r7r
Type: github-advisory

## Affected
- Packagist: `baserproject/basercms` — affected >=0 <5.2.3

## Details
### Details
The application's restore function allows users to upload a `.zip` file, which is then automatically extracted. A PHP file inside the archive is included using `require_once` without validating or restricting the filename. An attacker can craft a malicious PHP file within the zip and achieve arbitrary code execution when it is included.

Vector: Malicious ZIP upload + insecure `require_once`

### PoC
1. Restore backup
   ![image](https://github.com/user-attachments/assets/9e59768a-4a8e-472d-aaef-5d54546080f6)
1. Load file shell (insecure `require_once`)
   ![image](https://github.com/user-attachments/assets/8f7919a2-c7f3-4ae1-af6c-1b0057e4ba22)
   ![image](https://github.com/user-attachments/assets/c10ef049-459d-429e-a608-8fb220c3387f)

### Impact
Remote Code Execution (RCE)

## References
- https://github.com/baserproject/basercms/security/advisories/GHSA-hv78-cwp4-8r7r
- https://nvd.nist.gov/vuln/detail/CVE-2025-32957
- https://basercms.net/security/JVN_20837860
- https://github.com/baserproject/basercms
- https://github.com/baserproject/basercms/releases/tag/5.2.3
