# [H] CVE-2024-28054

## Summary
Severity: High
Advisory: CVE-2024-28054
CVSS: 7.4 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2024-03-18
Source: https://osv.dev/vulnerability/CVE-2024-28054
Type: osv

## Details
Amavis before 2.12.3 and 2.13.x before 2.13.1, in part because of its use of MIME-tools, has an Interpretation Conflict (relative to some mail user agents) when there are multiple boundary parameters in a MIME email message. Consequently, there can be an incorrect check for banned files or malware.

## References
- https://gitlab.com/amavis/amavis/-/raw/v2.13.1/README_FILES/README.CVE-2024-28054
- https://lists.amavis.org/pipermail/amavis-users/2024-March/006811.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/6J2MK2CS3KNJOS66QLW2MBJ4PIDLWJP5/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/XQQQQPTZ5JHXTUCYUXZHY6RZJ6VOGOAJ/
- https://metacpan.org/pod/MIME::Tools
- https://www.amavis.org/release-notes.txt
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/28xxx/CVE-2024-28054.json
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/6J2MK2CS3KNJOS66QLW2MBJ4PIDLWJP5/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/CDF6M3UXP45INVSWB4HXEDZH35CVZIJ4/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/XQQQQPTZ5JHXTUCYUXZHY6RZJ6VOGOAJ/
- https://nvd.nist.gov/vuln/detail/CVE-2024-28054
- https://gitlab.com/amavis/amavis/-/issues/112
