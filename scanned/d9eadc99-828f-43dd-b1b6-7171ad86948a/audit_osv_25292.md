# [M] Uncontrolled data used in content resolution

## Summary
Severity: Medium
Advisory: CVE-2023-33188
Aliases: GHSA-g38r-4cf6-3v32
CVSS: 6.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:N/A:L)
Published: 2023-05-27
Source: https://osv.dev/vulnerability/CVE-2023-33188
Type: osv

## Details
Omni-notes is an open source note-taking application for Android. The Omni-notes Android app had an insufficient path validation vulnerability when displaying the details of a note received through an externally-provided intent. The paths of the note's attachments were not properly validated, allowing malicious or compromised applications in the same device to force Omni-notes to copy files from its internal storage to its external storage directory, where they would have become accessible to any component with permission to read the external storage. Updating to the newest version (6.2.7) of Omni-notes Android fixes this vulnerability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/33xxx/CVE-2023-33188.json
- https://github.com/federicoiosue/Omni-Notes/security/advisories/GHSA-g38r-4cf6-3v32
- https://nvd.nist.gov/vuln/detail/CVE-2023-33188
