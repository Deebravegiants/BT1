# [H] React Native Document Picker Directory Traversal vulnerability

## Summary
Severity: High
Advisory: GHSA-pmgm-h3cc-m4hj
CVE: CVE-2024-25466
CWE: CWE-26
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:L/I:H/A:H (CVSS_V3)
Published: 2024-02-16
Source: https://github.com/advisories/GHSA-pmgm-h3cc-m4hj
Type: github-advisory

## Affected
- npm: `react-native-document-picker` — affected >=9.0.0 <9.1.1
- npm: `react-native-document-picker` — affected >=0 <8.2.2

## Details
Directory Traversal vulnerability in React Native Document Picker before 8.2.2 and 9.x before 9.1.1 allows a local attacker to execute arbitrary code via a crafted script to the Android library component.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-25466
- https://github.com/rnmods/react-native-document-picker/pull/698
- https://github.com/rnmods/react-native-document-picker/commit/1ae7cb217d23a551bff86ad10c7ae6f5e074490f
- https://github.com/rnmods/react-native-document-picker/commit/ad0b5e58252eba56a5a3b22311a66ffa5e65cffe
- https://github.com/FixedOctocat/CVE-2024-25466/tree/main
- https://github.com/rnmods/react-native-document-picker
- https://github.com/rnmods/react-native-document-picker/blob/0be5a70c3b456e35c2454aaf4dc8c2d40eb2ab47/android/src/main/java/com/reactnativedocumentpicker/RNDocumentPickerModule.java
- https://github.com/rnmods/react-native-document-picker/releases/tag/v8.2.2
