# [H] Whole-script approval in Jenkins Script Security Plugin vulnerable to SHA-1 collisions

## Summary
Severity: High
Advisory: GHSA-fv42-mx39-6fpw
CVE: CVE-2022-45379
CWE: CWE-326, CWE-328
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-11-16
Source: https://github.com/advisories/GHSA-fv42-mx39-6fpw
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:script-security` — affected >=0 <1190.v65867a_a_47126

## Details
Script Security Plugin 1189.vb_a_b_7c8fd5fde and earlier stores whole-script approvals as the [SHA-1 hash](https://en.wikipedia.org/wiki/SHA-1) of the approved script. SHA-1 no longer meets the security standards for producing a cryptographically secure message digest.

Script Security Plugin 1190.v65867a_a_47126 uses SHA-512 for new whole-script approvals. Previously approved scripts will have their SHA-1 based whole-script approval replaced with a corresponding SHA-512 whole-script approval when the script is next used.

Whole-script approval only stores the SHA-1 or SHA-512 hash, so it is not possible to migrate all previously approved scripts automatically on startup.

Administrators concerned about SHA-1 collision attacks on the whole-script approval feature are able to revoke all previous (SHA-1) script approvals on the In-Process Script Approval page.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-45379
- https://github.com/jenkinsci/script-security-plugin/commit/65867aa471265a16198b92fb439782ba3554da66
- https://github.com/jenkinsci/script-security-plugin
- https://www.jenkins.io/security/advisory/2022-11-15/#SECURITY-2564
- http://www.openwall.com/lists/oss-security/2022/11/15/4
