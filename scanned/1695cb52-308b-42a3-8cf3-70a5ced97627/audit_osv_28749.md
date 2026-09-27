# [C] CVE-2024-36057

## Summary
Severity: Critical
Advisory: CVE-2024-36057
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-07
Source: https://osv.dev/vulnerability/CVE-2024-36057
Type: osv

## Details
Koha Library before 23.05.10 fails to sanitize user-controllable filenames prior to unzipping, leading to remote code execution. The line "qx/unzip $filename -d $dirname/;" in upload-cover-image.pl is vulnerable to command injection via shell metacharacters because input data can be controlled by an attacker and is directly included in a system command, i.e., an attack can occur via malicious filenames after uploading a .zip file and clicking Process Images.

## References
- https://github.com/hacklantic/Research/tree/main/CVE-2024-36057
- https://gitlab.com/koha-community/Koha/-/blob/23.05.x/misc/release_notes/release_notes_23_05_10.md
- https://gitlab.com/koha-community/Koha/-/blob/23.05.x/misc/release_notes/release_notes_23_05_11.md
- https://koha-community.org/koha-22-05-22-released/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/36xxx/CVE-2024-36057.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-36057
