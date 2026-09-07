# [H] Maliciously Crafted Model Archive Can Lead To Arbitrary File Write

## Summary
Severity: High
Advisory: GHSA-4365-fhm5-qcrx
CVE: CVE-2021-41127
CWE: CWE-22, CWE-23
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2021-10-22
Source: https://github.com/advisories/GHSA-4365-fhm5-qcrx
Type: github-advisory

## Affected
- PyPI: `rasa` — affected >=0 <2.8.10

## Details
### Impact
An Archive Extraction (Zip Slip) vulnerability in the functionality that allows a user to load a trained model archive in Rasa 2.8.9 and older allows an attacker arbitrary write capability within specific directories using a malicious crafted archive file.

### Patches
The vulnerability is fixed in Rasa 2.8.10

### Workarounds
Mitigating steps for vulnerable end users are to ensure that they do not upload untrusted model files, and restrict CLI or API endpoint access where a malicious actor could target a deployed Rasa instance.

### For more information
If you have any questions or comments about this advisory:
* Email [the Rasa Security Team](mailto:security@rasa.com)

## References
- https://github.com/RasaHQ/rasa/security/advisories/GHSA-4365-fhm5-qcrx
- https://github.com/RasaHQ/rasa/commit/1b6b502f52d73b4f8cd1959ce724b8ad0eb33989
- https://github.com/RasaHQ/rasa
- https://github.com/pypa/advisory-database/tree/main/vulns/rasa/PYSEC-2021-381.yaml
