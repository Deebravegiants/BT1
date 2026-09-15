# [M] OctoPrint vulnerable to possible file extraction via upload endpoints

## Summary
Severity: Medium
Advisory: GHSA-m9jh-jf9h-x3h2
CVE: CVE-2025-48067
CWE: CWE-73
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:C/C:L/I:N/A:L (CVSS_V3)
Published: 2025-06-10
Source: https://github.com/advisories/GHSA-m9jh-jf9h-x3h2
Type: github-advisory

## Affected
- PyPI: `OctoPrint` — affected >=0 <1.11.2

## Details
### Impact

OctoPrint versions up until and including 1.11.1 contain a vulnerability that allows an attacker with the `FILE_UPLOAD` permission to exfiltrate files from the host that OctoPrint has read access to, by moving them into the upload folder where they then can be downloaded from.

The primary risk lies in the potential exfiltration of secrets stored inside OctoPrint's config, or further system files. By removing important runtime files, this could also be used to impact the availability of the host. Given that the attacker requires a user account with file upload permissions, the actual impact of this should however hopefully be minimal in most cases.

### Patches

The vulnerability has been patched in version 1.11.2.

### Details

A specially crafted HTTP Request to an affected upload endpoint that contains some form inputs only supposed to be used internally can be used to make OctoPrint move a file that it thinks is a freshly uploaded temporary one into its upload folder.

The following endpoints in OctoPrint are affected:

- `/api/files/{local|sdcard}`
- `/api/languages`
- `/plugin/backup/restore`
- `/plugin/pluginmanager/upload_file`

Further upload endpoints in third party plugins might be affected too.

The fix removes any internal-only form inputs from incoming requests in the central file upload processor component.

### Credits

This vulnerability was discovered and responsibly disclosed to OctoPrint by Jacopo Tediosi

## References
- https://github.com/OctoPrint/OctoPrint/security/advisories/GHSA-m9jh-jf9h-x3h2
- https://nvd.nist.gov/vuln/detail/CVE-2025-48067
- https://github.com/OctoPrint/OctoPrint/commit/9984b20773f5895a432f965b759999b16c57f7d8
- https://github.com/OctoPrint/OctoPrint
