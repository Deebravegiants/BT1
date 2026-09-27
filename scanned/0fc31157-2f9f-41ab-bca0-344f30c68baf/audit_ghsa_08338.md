# [H] FacturaScripts Vulnerable to Remote Code Execution (RCE) via Zip Slip in Plugin Upload Mechanism

## Summary
Severity: High
Advisory: GHSA-3pgc-xqg9-cfr6
CVE: CVE-2026-27891
CWE: CWE-20, CWE-434
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-07
Source: https://github.com/advisories/GHSA-3pgc-xqg9-cfr6
Type: github-advisory

## Affected
- Packagist: `facturascripts/facturascripts` — affected >=0

## Details
### Summary
A Critical vulnerability exists in the `Plugins::add()` function. The system fails to properly validate the file paths within uploaded ZIP archives. This allows an attacker to perform a Zip Slip attack, leading to Arbitrary File Write and Remote Code Execution (RCE) by overwriting sensitive .php files outside the designated plugins directory.

### Details
The vulnerability is located in Plugins.php. While the `testZipFile` function attempts to validate that the ZIP contains only one root folder, it does not sanitize or validate the individual file paths within that folder.
```js
// Vulnerable logic in Plugins.php
for ($index = 0; $index < $zipFile->numFiles; $index++) {
    $data = $zipFile->statIndex($index);
    $path = explode('/', $data['name']);
    if (count($path) > 1) {
        $folders[$path[0]] = $path[0];
    }
} 
```
An attacker can bypass this check by naming a file `ValidPluginName/../../shell.php`. The explode function will see ValidPluginName as the root folder, satisfying the `count($folders) != 1` check. However, during extraction, the `../../` sequence triggers a path traversal, allowing the file to be written anywhere the web server has permissions the root directory.
### PoC
Prepare Malicious ZIP: Use a tool (like evilarc) or a script to create a ZIP file where one of the entries is named: `MyPlugin/../../rce.php`
Inject Payload: Inside rce.php, put a simple shell: 
`<?php system($_GET['cmd']); ?>`
Upload: Navigate to the "Add Plugin" section in FacturaScripts and upload the malicious ZIP.
Execution: Access the shell via https://target.com/rce.php?cmd=whoami.

### Impact
Confidentiality: High (Attacker can read all database configs and files).
Integrity: High (Attacker can modify any file on the server).
Availability: High (Attacker can delete the entire installation).
> https://github.com/ZeroXJacks/CVEs/blob/main/2026/CVE-2026-27891.md

## References
- https://github.com/NeoRazorX/facturascripts/security/advisories/GHSA-3pgc-xqg9-cfr6
- https://github.com/NeoRazorX/facturascripts
