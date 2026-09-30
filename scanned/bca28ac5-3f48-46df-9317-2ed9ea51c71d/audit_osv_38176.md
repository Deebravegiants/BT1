# [C] text-generation-webui affected by Remote Code Execution (RCE) through Path Traversal at "Session -> Save extention settings to user_data/settings.yaml".

## Summary
Severity: Critical
Advisory: CVE-2026-35050
Aliases: GHSA-jg96-p5p6-q3cv
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-04-06
Source: https://osv.dev/vulnerability/CVE-2026-35050
Type: osv

## Details
text-generation-webui is an open-source web interface for running Large Language Models. Prior to 4.1.1, users can save extention settings in "py" format and in the app root directory. This allows to overwrite python files, for instance the "download-model.py" file could be overwritten. Then, this python file can be triggered to get executed from "Model" menu when requesting to download a new model. This vulnerability is fixed in 4.1.1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/35xxx/CVE-2026-35050.json
- https://github.com/oobabooga/text-generation-webui/security/advisories/GHSA-jg96-p5p6-q3cv
- https://nvd.nist.gov/vuln/detail/CVE-2026-35050
