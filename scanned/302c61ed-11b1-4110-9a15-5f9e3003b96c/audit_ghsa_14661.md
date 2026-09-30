# [H] changedetection.io Vulnerable to Improper Input Validation Leading to LFR/Path Traversal

## Summary
Severity: High
Advisory: GHSA-j5vv-6wjg-cfr8
CVE: CVE-2024-56509
CWE: CWE-200, CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2024-12-27
Source: https://github.com/advisories/GHSA-j5vv-6wjg-cfr8
Type: github-advisory

## Affected
- PyPI: `changedetection.io` — affected >=0 <0.48.05

## Details
### Summary
Improper input validation in the application can allow attackers to perform local file read (LFR) or path traversal attacks. These vulnerabilities occur when user input is used to construct file paths without adequate sanitization or validation. For example, using `file:../../../etc/passwd` or `file: ///etc/passwd` can bypass weak validations and allow unauthorized access to sensitive files. Even though this has been addressed in previous patch, it is still insufficient.

### Details
The check in this line of code is insufficient.
```
if re.search(r'^file:/', url.strip(), re.IGNORECASE):
```
The attacker can still bypass this by using:
-`file:../../../../etc/passwd`
-`file: ///etc/passwd` (with space before /)

### PoC
- Open up a changedetection.io instance with a webdriver configured.
- Create a new watch with `file:../../../../etc/passwd`.
- Check the watch preview.
- The contents of `/etc/passwd` should pop out.

### Screenshots
![image](https://github.com/user-attachments/assets/55c34f2e-cafb-4a7a-a7ef-ec222e3f519b)
![image](https://github.com/user-attachments/assets/d41189f5-7bf2-48b5-9ce3-c26f79cefeda)

## References
- https://github.com/dgtlmoon/changedetection.io/security/advisories/GHSA-j5vv-6wjg-cfr8
- https://nvd.nist.gov/vuln/detail/CVE-2024-56509
- https://github.com/dgtlmoon/changedetection.io/commit/4419bc0e61d0b03c588bd573a3602bbcfd953671
- https://github.com/dgtlmoon/changedetection.io/commit/f7e9846c9b40a229813d19cdb66bf60fbe5e6a2a
- https://github.com/dgtlmoon/changedetection.io
