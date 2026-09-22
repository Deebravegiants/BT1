# [C] RSA PKCS#1 decryption vulnerability with prepending zeros in jsrsasign

## Summary
Severity: Critical
Advisory: GHSA-xxxq-chmp-67g4
CVE: CVE-2020-14967
CWE: CWE-119
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2020-06-26
Source: https://github.com/advisories/GHSA-xxxq-chmp-67g4
Type: github-advisory

## Affected
- npm: `jsrsasign` — affected >=0 <8.0.18

## Details
### Impact
Jsrsasign supports RSA PKCS#1 v1.5 (i.e. RSAES-PKCS1-v1_5) and RSA-OAEP encryption and decryption. Its encrypted message is represented as BigInteger. When there is a valid encrypted message, a crafted message with prepending zeros can be decrypted by this vulnerability.

- If you don't use RSA PKCS1-v1_5 or RSA-OAEP decryption, this vulnerability is not affected.
- Risk to forge contents of encrypted message is very low.
- Risk to raise memory corruption is low since jsrsasign uses BigInteger class.

### Patches
Users using RSA PKCS1-v1_5 or RSA-OAEP decryption should upgrade to 8.0.18.

### Workarounds
Reject RSA PKCS1-v1_5 or RSA-OAEP encrypted message with unnecessary prepending zeros.

### References
https://nvd.nist.gov/vuln/detail/CVE-2020-14967
https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2020-14967
https://vuldb.com/?id.157124
https://kjur.github.io/jsrsasign/api/symbols/KJUR.crypto.Cipher.html#.decrypt
https://github.com/kjur/jsrsasign/issues/439

## References
- https://github.com/kjur/jsrsasign/security/advisories/GHSA-xxxq-chmp-67g4
- https://nvd.nist.gov/vuln/detail/CVE-2020-14967
- https://github.com/kjur/jsrsasign/issues/439
- https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2020-14967
- https://github.com/kjur/jsrsasign
- https://github.com/kjur/jsrsasign/releases/tag/8.0.17
- https://github.com/kjur/jsrsasign/releases/tag/8.0.18
- https://kjur.github.io/jsrsasign
- https://kjur.github.io/jsrsasign/api/symbols/KJUR.crypto.Cipher.html#.decrypt
- https://security.netapp.com/advisory/ntap-20200724-0001
- https://vuldb.com/?id.157124
- https://www.npmjs.com/package/jsrsasign
