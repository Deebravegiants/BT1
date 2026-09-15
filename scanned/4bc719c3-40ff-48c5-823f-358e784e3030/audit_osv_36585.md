# [M] OpenEMR Vulnerable to Arbitrary File Exfiltration via Fax Endpoint

## Summary
Severity: Medium
Advisory: CVE-2026-24488
Aliases: GHSA-765x-8v97-c7g8
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-02-27
Source: https://osv.dev/vulnerability/CVE-2026-24488
Type: osv

## Details
OpenEMR is a free and open source electronic health records and medical practice management application. In versions up to and including 8.0.0, an arbitrary file exfiltration vulnerability in the fax sending endpoint allows any authenticated user to read and transmit any file on the server (including database credentials, patient documents, system files, and source code) via fax to an attacker-controlled phone number. The vulnerability exists because the endpoint accepts arbitrary file paths from user input and streams them to the fax gateway without path restrictions or authorization checks. As of time of publication, no known patched versions are available.

## References
- https://github.com/openemr/openemr/blob/v7_0_4/interface/modules/custom_modules/oe-module-faxsms/src/Controller/EtherFaxActions.php#L177-L221
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/24xxx/CVE-2026-24488.json
- https://github.com/openemr/openemr/security/advisories/GHSA-765x-8v97-c7g8
- https://nvd.nist.gov/vuln/detail/CVE-2026-24488
