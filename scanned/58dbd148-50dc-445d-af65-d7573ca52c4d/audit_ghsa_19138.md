# [H] MobSF Partial Denial of Service (DoS)

## Summary
Severity: High
Advisory: GHSA-jrm8-xgf3-fwqr
CVE: CVE-2025-24804
CWE: CWE-1287
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-02-05
Source: https://github.com/advisories/GHSA-jrm8-xgf3-fwqr
Type: github-advisory

## Affected
- PyPI: `mobsf` — affected >=0 <4.3.1

## Details
# Partial Denial of Service (DoS)

**Product:** MobSF
**Version:** v4.2.9
**CWE-ID:** CWE-1287: Improper Validation of Specified Type of Input
**CVSS vector v.4.0:** 6.9 (AV:N/AC:L/AT:N/PR:N/UI:P/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
**CVSS vector v.3.1:** 6.5 (AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
**Description:**  DoS in the Scans Results and iOS Dynamic Analyzer functionality 
**Impact:** Leveraging this vulnerability would make Scans Results and iOS Dynamic Analyzer pages unavailable.
**Vulnerable component:** urls.py
https://github.com/MobSF/Mobile-Security-Framework-MobSF/blob/d1d3b7a9aeb1a8c8c7c229a3455b19ade9fa8fe0/mobsf/MobSF/urls.py#L401
**Exploitation conditions:** A malicious application was uploaded to the MobSF.
**Mitigation:** Check the uploaded bundle IDs against the regex.
**Researcher: Oleg Surnin (Positive Technologies)**

## Research

Researcher discovered zero-day vulnerability Partial Denial of Service (DoS) in MobSF in the Scans Results and iOS Dynamic Analyzer functionality.
According to Apple's documentation for bundle ID's, it must contain only alphanumeric characters (A–Z, a–z, and 0–9), hyphens (-), and periods (.).
(https://developer.apple.com/documentation/bundleresources/information-property-list/cfbundleidentifier)
However, an attacker can manually modify this value in `Info.plist` file and add special characters to the `<key>CFBundleIdentifier</key>` value.
In the `urls.py` file URL rules are defined.
https://github.com/MobSF/Mobile-Security-Framework-MobSF/blob/d1d3b7a9aeb1a8c8c7c229a3455b19ade9fa8fe0/mobsf/MobSF/urls.py#L401

*Listing 3.*
```
bundle_id_regex = r'(?P<bundle_id>([a-zA-Z0-9]{1}[\w.-]{1,255}))$'

# skip code
re_path(fr'^ios/view_report/{bundle_id_regex}',
                ios_view_report.ç,
                name='ios_view_report'),
```

When the application parses the wrong characters in the bundle ID, it encounters an error.
As a result, it will not display content and will throw a 500 error instead. The only way to make the pages work again is to manually remove the malicious application from the system.

## Vulnerability reproduction

To reproduce the vulnerability, follow the steps described below.

•	Unzip the IPA file of any iOS application.

*Listing 4. Unzipping the file*
```
unzip test.ipa
```

•	Modify the value of `<key>CFBundleIdentifier</key>` by adding restricted characters in the `Info.plist` file.

<img width="364" alt="image-6" src="https://github.com/user-attachments/assets/97dce68a-a5e2-4048-b5c8-3090146a9635" />

*Figure 7. Example with `'` character`


•	Zip the modified IPA file.

*Listing 5. Zipping the file*
```
zip -r dos.ipa Payload/
```

•	Upload the modified IPA file to Static Analysis and wait until it finished
•	Open the following pages:
`http://mobsf/recent_scans/`
`http://mobsf/ios/dynamic_analysis/`

<img width="1119" alt="image-7" src="https://github.com/user-attachments/assets/a7a9ae2e-cd84-4ec8-8132-25140a209ca0" />

*Figure 8. DoS Example*

<img width="1141" alt="image-8" src="https://github.com/user-attachments/assets/a76e03ae-b4c6-4003-a145-c1fa4c88a7a5" />
 
*Figure 9. DoS Example*


_________________

### Please, assign all credits to Oleg Surnin (Positive Technologies)

## References
- https://github.com/MobSF/Mobile-Security-Framework-MobSF/security/advisories/GHSA-jrm8-xgf3-fwqr
- https://nvd.nist.gov/vuln/detail/CVE-2025-24804
- https://github.com/MobSF/Mobile-Security-Framework-MobSF/commit/05206e72cae35b311615a70e51e1a946955c5e83
- https://developer.apple.com/documentation/bundleresources/information-property-list/cfbundleidentifier
- https://github.com/MobSF/Mobile-Security-Framework-MobSF
- https://github.com/MobSF/Mobile-Security-Framework-MobSF/blob/d1d3b7a9aeb1a8c8c7c229a3455b19ade9fa8fe0/mobsf/MobSF/urls.py#L401
