# [H] ECDSA signature validation vulnerability by accepting wrong ASN.1 encoding in jsrsasign

## Summary
Severity: High
Advisory: GHSA-p8c3-7rj8-q963
CVE: CVE-2020-14966
CWE: CWE-347
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2020-06-26
Source: https://github.com/advisories/GHSA-p8c3-7rj8-q963
Type: github-advisory

## Affected
- npm: `jsrsasign` — affected >=4.0.0 <8.0.19

## Details
### Impact
Jsrsasign supports ECDSA signature validation which signature value is represented by ASN.1 DER encoding. This vulnerablity may accept a wrong ASN.1 DER encoded ECDSA signature such as:

- wrong multi-byte ASN.1 length of TLV (ex. 0x820045 even though 0x45 is correct)
- prepending zeros with ASN.1 INTEGER value (ex. 0x00000123 even though 0x0123 is correct)
- appending zeros to signature of ASN.1 TLV (ex. 0x3082....1fbc000000 even though 0x3082....1fbc, appending zeros are ignored.)

This vulnerability was fixed by strict ASN.1 DER checking. 

Here is an assessment of this vulnerability:

- If you are not use ECDSA signature validation, this vulnerability is not affected.
- Not ASN.1 format signature like just concatenation of R and S value is not affected such as Bitcoin.
- This vulnerability is affected to all ECC curve parameters.
- Risk to accept a forged or crafted message to be signed is low.
- Risk to raise memory corruption is low since jsrsasign uses BigInteger class.
- ECDSA signatures semantically the same to valid one may be accepted as valid. There are many malleable variants.

As discussed [here](https://crypto.stackexchange.com/questions/24862/ber-or-der-x9-62-for-ecdsa-signature), there is no standards like X9.62 which requires ASN.1 DER. So ASN.1 BER can be applied to ECDSA however most of implementations like OpenSSL do strict ASN.1 DER checking.

### Patches
Users using ECDSA signature validation should upgrade to 8.0.19.

### Workarounds
Do strict ASN.1 DER checking for ASN.1 encoded ECDSA signature value.

### References
https://nvd.nist.gov/vuln/detail/CVE-2020-14966
https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2020-14966
https://vuldb.com/?id.157123
https://github.com/kjur/jsrsasign/issues/437
https://kjur.github.io/jsrsasign/api/symbols/KJUR.crypto.ECDSA.html
https://kjur.github.io/jsrsasign/api/symbols/ASN1HEX.html#.checkStrictDER
https://www.itu.int/rec/T-REC-X.690

## References
- https://github.com/kjur/jsrsasign/security/advisories/GHSA-p8c3-7rj8-q963
- https://nvd.nist.gov/vuln/detail/CVE-2020-14966
- https://github.com/kjur/jsrsasign/issues/437
- https://github.com/kjur/jsrsasign/commit/6087412d072a57074d3c4c1b40bdde0460d53a7f
- https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2020-14966
- https://github.com/kjur/jsrsasign
- https://github.com/kjur/jsrsasign/releases/tag/8.0.17
- https://github.com/kjur/jsrsasign/releases/tag/8.0.18
- https://kjur.github.io/jsrsasign
- https://kjur.github.io/jsrsasign/api/symbols/ASN1HEX.html#.checkStrictDER
- https://kjur.github.io/jsrsasign/api/symbols/KJUR.crypto.ECDSA.html
- https://security.netapp.com/advisory/ntap-20200724-0001
- https://vuldb.com/?id.157123
- https://www.npmjs.com/package/jsrsasign
