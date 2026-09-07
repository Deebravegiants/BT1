# [H] Marvin Attack of RSA and RSAOAEP decryption in jsrsasign

## Summary
Severity: High
Advisory: GHSA-rh63-9qcf-83gf
CVE: CVE-2024-21484
CWE: CWE-203
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:N/A:L (CVSS_V3)
Published: 2024-01-19
Source: https://github.com/advisories/GHSA-rh63-9qcf-83gf
Type: github-advisory

## Affected
- npm: `jsrsasign` — affected >=0 <11.0.0

## Details
### Impact
RSA PKCS#1.5 or RSAOAEP ciphertexts may be decrypted by this Marvin attack vulnerability.

### Patches
update to jsrsasign 11.0.0.

### Workarounds
Find and replace RSA and RSAOAEP decryption with other crypto library.

### References
https://people.redhat.com/~hkario/marvin/
https://github.com/kjur/jsrsasign/issues/598
https://security.snyk.io/vuln/SNYK-JAVA-ORGWEBJARSNPM-6070732
https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2024-21484

## References
- https://github.com/kjur/jsrsasign/security/advisories/GHSA-rh63-9qcf-83gf
- https://nvd.nist.gov/vuln/detail/CVE-2024-21484
- https://github.com/kjur/jsrsasign/issues/598
- https://github.com/kjur/jsrsasign
- https://github.com/kjur/jsrsasign/releases/tag/11.0.0
- https://people.redhat.com/~hkario/marvin
- https://security.snyk.io/vuln/SNYK-JAVA-ORGWEBJARSBOWER-6070734
- https://security.snyk.io/vuln/SNYK-JAVA-ORGWEBJARSBOWERGITHUBKJUR-6070733
- https://security.snyk.io/vuln/SNYK-JAVA-ORGWEBJARSNPM-6070732
- https://security.snyk.io/vuln/SNYK-JS-JSRSASIGN-6070731
