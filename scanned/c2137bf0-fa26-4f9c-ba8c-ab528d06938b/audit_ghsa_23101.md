# [C] LibreNMS arbitrary OS commands execution

## Summary
Severity: Critical
Advisory: GHSA-62q7-qj6g-gvr7
CVE: CVE-2018-20434
CWE: CWE-78
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-62q7-qj6g-gvr7
Type: github-advisory

## Affected
- Packagist: `librenms/librenms` — affected 1.46

## Details
LibreNMS 1.46 allows remote attackers to execute arbitrary OS commands by using the `$_POST['community']` parameter to `html/pages/addhost.inc.php` during creation of a new device, and then making a `/ajax_output.php?id=capture&format=text&type=snmpwalk&hostname=localhost request that triggers html/includes/output/capture.inc.php` command mishandling.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-20434
- https://drive.google.com/file/d/1LcGmOY8x-TG-wnNr-cM_f854kxk0etva/view?usp=sharing
- https://gist.github.com/mhaskar/516df57aafd8c6e3a1d70765075d372d
- https://github.com/librenms/librenms
- https://shells.systems/librenms-v1-46-remote-code-execution-cve-2018-20434
