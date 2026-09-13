# [H] Timing Attack Vulnerability in gaizhenbiao/chuanhuchatgpt

## Summary
Severity: High
Advisory: CVE-2024-5124
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-06-06
Source: https://osv.dev/vulnerability/CVE-2024-5124
Type: osv

## Details
A timing attack vulnerability exists in the gaizhenbiao/chuanhuchatgpt repository, specifically within the password comparison logic. The vulnerability is present in version 20240310 of the software, where passwords are compared using the '=' operator in Python. This method of comparison allows an attacker to guess passwords based on the timing of each character's comparison. The issue arises from the code segment that checks a password for a particular username, which can lead to the exposure of sensitive information to an unauthorized actor. An attacker exploiting this vulnerability could potentially guess user passwords, compromising the security of the system.

## References
- https://huntr.com/bounties/e85ec077-930a-4597-975f-9341d2805641
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/5xxx/CVE-2024-5124.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-5124
- https://github.com/gaizhenbiao/chuanhuchatgpt/commit/e46ec4ecd896bc3c88eb9a2f44e8593f3c6761b4
