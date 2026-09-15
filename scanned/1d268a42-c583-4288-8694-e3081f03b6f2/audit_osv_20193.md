# [C] CVE-2021-3210

## Summary
Severity: Critical
Advisory: CVE-2021-3210
CVSS: 9.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H)
Published: 2021-02-19
Source: https://osv.dev/vulnerability/CVE-2021-3210
Type: osv

## Details
components/Modals/HelpTexts/GenericAll/GenericAll.jsx in Bloodhound <= 4.0.1 allows remote attackers to execute arbitrary system commands when the victim imports a malicious data file containing JavaScript in the objectId parameter.

## References
- https://github.com/BloodHoundAD/BloodHound/issues/338
- https://github.com/BloodHoundAD/BloodHound/blob/338e197dc4b7a1ee929c335141172ada5bc80800/src/components/Modals/HelpModal.jsx#L57
- https://github.com/BloodHoundAD/BloodHound/blob/338e197dc4b7a1ee929c335141172ada5bc80800/src/components/Modals/HelpTexts/GenericAll/GenericAll.jsx#L31-L37
