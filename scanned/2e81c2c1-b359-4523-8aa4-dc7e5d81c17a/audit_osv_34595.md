# [M] text-generation-webui allows arbitrary file read via symbolic link upload

## Summary
Severity: Medium
Advisory: CVE-2025-62364
Aliases: GHSA-66rw-q8w5-c2hg
CVSS: 6.2 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2025-10-13
Source: https://osv.dev/vulnerability/CVE-2025-62364
Type: osv

## Details
text-generation-webui is an open-source web interface for running Large Language Models. In versions through 3.13, a Local File Inclusion vulnerability exists in the character picture upload feature. An attacker can upload a text file containing a symbolic link to an arbitrary file path. When the application processes the upload, it follows the symbolic link and serves the contents of the targeted file through the web interface. This allows an unauthenticated attacker to read sensitive files on the server, potentially exposing system configurations, credentials, and other confidential information. This vulnerability is fixed in 3.14. No known workarounds exist.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/62xxx/CVE-2025-62364.json
- https://github.com/oobabooga/text-generation-webui/security/advisories/GHSA-66rw-q8w5-c2hg
- https://nvd.nist.gov/vuln/detail/CVE-2025-62364
- https://github.com/oobabooga/text-generation-webui/commit/282aa1918907fceec7f903d3dc2bc8492ce8e885
