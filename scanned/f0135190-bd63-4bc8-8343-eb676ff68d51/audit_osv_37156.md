# [M] Open Forms possible to view submission details of other people than intended

## Summary
Severity: Medium
Advisory: CVE-2026-28803
Aliases: GHSA-2g49-rfm6-5qj5
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-03-11
Source: https://osv.dev/vulnerability/CVE-2026-28803
Type: osv

## Details
Open Forms allows users create and publish smart forms. Prior to 3.3.13 and 3.4.5, to be able to cosign, the cosigner receives an e-mail with instructions or a deep-link to start the cosign flow. The submission reference is communicated so that the user can retrieve the submission to be cosigned. Attackers can guess a code or modify the received code to look up arbitrary submissions, after logging in (with DigiD/eHerkenning/... depending on form configuration). This vulnerability is fixed in 3.3.13 and 3.4.5.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/28xxx/CVE-2026-28803.json
- https://github.com/open-formulieren/open-forms/security/advisories/GHSA-2g49-rfm6-5qj5
- https://nvd.nist.gov/vuln/detail/CVE-2026-28803
