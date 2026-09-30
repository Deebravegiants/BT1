# [C] Local File Inclusion in parisneo/lollms-webui

## Summary
Severity: Critical
Advisory: CVE-2024-1600
CVSS: 9.3 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:L)
Published: 2024-04-10
Source: https://osv.dev/vulnerability/CVE-2024-1600
Type: osv

## Details
A Local File Inclusion (LFI) vulnerability exists in the parisneo/lollms-webui application, specifically within the `/personalities` route. An attacker can exploit this vulnerability by crafting a URL that includes directory traversal sequences (`../../`) followed by the desired system file path, URL encoded. Successful exploitation allows the attacker to read any file on the filesystem accessible by the web server. This issue arises due to improper control of filename for include/require statement in the application.

## References
- https://huntr.com/bounties/29ec621a-bd69-4225-ab0f-5bb8a1d10c67
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/1xxx/CVE-2024-1600.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-1600
- https://github.com/parisneo/lollms-webui/commit/49b0332e98d42dd5204dda53dee410b160106265
