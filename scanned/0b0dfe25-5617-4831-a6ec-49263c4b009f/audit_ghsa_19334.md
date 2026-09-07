# [M] TYPO3 Allows Unrestricted File Upload in File Abstraction Layer

## Summary
Severity: Medium
Advisory: GHSA-9hq9-cr36-4wpj
CVE: CVE-2025-47939
CWE: CWE-351, CWE-434
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:L (CVSS_V3)
Published: 2025-05-20
Source: https://github.com/advisories/GHSA-9hq9-cr36-4wpj
Type: github-advisory

## Affected
- Packagist: `typo3/cms-core` — affected >=9.0.0 <9.5.51
- Packagist: `typo3/cms-core` — affected >=10.0.0 <10.4.50
- Packagist: `typo3/cms-core` — affected >=11.0.0 <11.5.44
- Packagist: `typo3/cms-core` — affected >=12.0.0 <12.4.31
- Packagist: `typo3/cms-core` — affected >=13.0.0 <13.4.12

## Details
### Problem
By design, the file management module in TYPO3’s backend user interface has historically allowed the upload of any file type, with the exception of those that are directly executable in a web server context. This lack of restriction means it is possible to upload files that may be considered potentially harmful, such as executable binaries (e.g., `.exe` files), or files with inconsistent file extensions and MIME types (for example, a file incorrectly named with a `.png` extension but actually carrying the MIME type `application/zip`).

Although such files are not directly executable through the web server, their presence can introduce indirect risks. For example, third-party services such as antivirus scanners or malware detection systems might flag or block access to the website for end users if suspicious files are found. This could negatively affect the availability or reputation of the site.

### Solution
Update to TYPO3 versions 9.5.51 ELTS, 10.4.50 ELTS, 11.5.44 ELTS, 12.4.31 LTS, 13.4.12 LTS that fix the problem described.

> [!NOTE]
> The mitigation strategies outlined below apply broadly to all file uploads handled through TYPO3's File Abstraction Layer (FAL), not just those performed via the backend interface. This means that any extension or custom integration leveraging FAL will also be subject to the new validation rules and configuration options. Developers are advised to review the implications for their code and refer to the [documentation of that change](https://docs.typo3.org/c/typo3/cms-core/main/en-us/Changelog/12.4.x/Important-106240-EnforceFile-extensionsAndMime-typeConsistencyInFileAbstractionLayer.html) for guidance.

> [!IMPORTANT]
>
> **Strong security defaults - Manual actions required**
> 
> These versions introduce new configuration options to better control which files are permitted for upload and to improve consistency checks.
> 
> A new configuration option, `$GLOBALS['TYPO3_CONF_VARS']['SYS']['miscfile_ext']`, has been added. This option allows administrators to explicitly define which file extensions should be permitted that are not already part of the built-in text or media file groups - examples include archive formats such as `zip` or `xz`.
> 
> In addition, two new feature flags have been introduced to enhance security:
> * `security.system.enforceAllowedFileExtensions`, enforces the defined list of allowed file extensions. This flag is enabled by default in new TYPO3 installations, but remains disabled in existing installations to prevent breaking changes.
> * `security.system.enforceFileExtensionMimeTypeConsistency`, ensures that the uploaded file’s extension matches its actual MIME type, providing further validation of file integrity. This flag is active by default.
> 
> It is recommended to configure the allowed file extensions via `$GLOBALS['TYPO3_CONF_VARS']['SYS']['miscfile_ext']` and to enable the feature flag `security.system.enforceAllowedFileExtensions` to enforce the restriction.

### Credits
Thanks to Hamed Kohi for reporting this issue, and to TYPO3 core & security team member Oliver Hader for fixing it.

## References
- https://github.com/TYPO3/typo3/security/advisories/GHSA-9hq9-cr36-4wpj
- https://nvd.nist.gov/vuln/detail/CVE-2025-47939
- https://github.com/TYPO3-CMS/core/commit/c265beed6e2c01817c534a226e80e593400f8255
- https://github.com/TYPO3-CMS/core
- https://typo3.org/security/advisory/typo3-core-sa-2025-014
