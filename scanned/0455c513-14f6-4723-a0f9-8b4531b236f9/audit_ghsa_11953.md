# [H] Sharp has Unrestricted File Upload via Client-Controlled Validation Rules

## Summary
Severity: High
Advisory: GHSA-fr76-5637-w3g9
CVE: CVE-2026-33687
CWE: CWE-434
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-25
Source: https://github.com/advisories/GHSA-fr76-5637-w3g9
Type: github-advisory

## Affected
- Packagist: `code16/sharp` — affected >=0 <9.20.0

## Details
### Summary 
The `code16/sharp` Laravel admin panel package contains a vulnerability in its file upload endpoint that allows authenticated users to bypass all file type restrictions.

### Details
The upload endpoint within the `ApiFormUploadController` accepts a client-controlled `validation_rule` parameter. This parameter is directly passed into the Laravel validator without sufficient server-side enforcement. By intercepting the request and sending `validation_rule[]=file`, an attacker can completely bypass all MIME type and file extension restrictions. The vulnerable code is located in `src/Http/Controllers/Api/ApiFormUploadController.php` at line 24.

### Impact
This vulnerability leads to several critical security risks:

Attackers can upload arbitrary files, including PHP webshells, to the server. For more details on the package, visit: https://github.com/code16/sharp

MIME type and extension validation can be bypassed entirely via client-controlled rules. Review the CWE definition here: https://cwe.mitre.org/data/definitions/434.html

If the storage disk is configured to be publicly accessible, this can lead to Remote Code Execution (RCE). See the vendor repository: https://github.com/code16/sharp

(Note: Under default configurations, executing uploaded PHP files directly is not possible unless a public disk configuration is in place.)

### Patches
This issue has been addressed by removing the client-controlled validation rules and strictly defining upload rules server-side. The fix is available in pull request https://github.com/code16/sharp/pull/714.

### Workarounds
- Restrict Disk Access: Ensure that the storage disk used for Sharp uploads is strictly private. Under default configurations, an attacker cannot directly execute uploaded PHP files unless a public disk configuration is explicitly used. For more details on Laravel disk configurations, visit: https://laravel.com/docs/13.x/filesystem

### Credits
Reported by [zaurgsynv](https://github.com/zaurgsynv).

## References
- https://github.com/code16/sharp/security/advisories/GHSA-fr76-5637-w3g9
- https://nvd.nist.gov/vuln/detail/CVE-2026-33687
- https://github.com/code16/sharp/pull/714
- https://github.com/code16/sharp
- https://github.com/code16/sharp/releases/tag/v9.20.0
- https://laravel.com/docs/13.x/filesystem
