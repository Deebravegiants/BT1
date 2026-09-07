# [H] Unrestricted File Upload in Form Framework

## Summary
Severity: High
Advisory: GHSA-2r6j-862c-m2v2
CVE: CVE-2021-21355
CWE: CWE-434, CWE-552
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:H/A:L/E:F/RL:O/RC:C (CVSS_V3)
Published: 2021-03-23
Source: https://github.com/advisories/GHSA-2r6j-862c-m2v2
Type: github-advisory

## Affected
- Packagist: `typo3/cms-form` — affected >=8.0.0 <8.7.40
- Packagist: `typo3/cms-form` — affected >=9.0.0 <9.5.25
- Packagist: `typo3/cms-form` — affected >=10.0.0 <10.4.14
- Packagist: `typo3/cms-form` — affected >=11.0.0 <11.1.1
- Packagist: `typo3/cms-core` — affected >=10.0.0 <10.4.14
- Packagist: `typo3/cms-core` — affected >=11.0.0 <11.1.1
- Packagist: `typo3/cms-core` — affected >=9.0.0 <9.5.25
- Packagist: `typo3/cms` — affected >=10.0.0 <10.4.14
- Packagist: `typo3/cms` — affected >=11.0.0 <11.1.1
- Packagist: `typo3/cms` — affected >=9.0.0 <9.5.25

## Details
### Problem
Due to the lack of ensuring file extensions belong to configured allowed mime-types, attackers can upload arbitrary data with arbitrary file extensions - however, default _fileDenyPattern_ successfully blocked files like _.htaccess_ or _malicious.php_.

TYPO3 Extbase extensions, which implement a file upload and do not implement a custom _TypeConverter_ to transform uploaded files into _FileReference_ domain model objects are affected by the vulnerability as well, since the _UploadedFileReferenceConverter_ of _ext:form_ handles the file upload and will accept files of any mime-type which are persisted to the default location.

In any way, uploaded files are placed in the default location _/fileadmin/user_upload/_, in most scenarios keeping the submitted filename - which allows attackers to directly reference files, or even correctly guess filenames used by other individuals, disclosing this information.

No authentication is required to exploit this vulnerability.

### Solution
Update to TYPO3 versions 8.7.40, 9.5.25, 10.4.14, 11.1.1 that fix the problem described.

Type converter _UploadedFileReferenceConverter_ is not registered globally anymore and just handles uploaded files within the scope of the Form Framework. Guessable storage location has changed from _/fileadmin/user_upload/form\_\<random-hash\>/_ to _/fileadmin/form_uploads/<random-40-bit>_. Allowed mime-types must match expected file extensions (e.g. _application/pdf_ must be _.pdf_, and cannot be _.html_).

Extbase extensions, who rely on the global availability of the _UploadedFileReferenceConverter_ must now implement a custom _TypeConverter_ to handle file uploads or explicitly implement the ext:form _UploadedFileReferenceConverter_ with appropriate setting for accepted mime-types.

### Credits
Thanks to Sebastian Michaelsen, Marc Lindemann, Oliver Eglseder, Markus Volkmer, Jakob Kunzmann, Johannes Regner, Richie Lee who reported this issue, and to TYPO3 core & security team members Oliver Hader & Benni Mack, as well as TYPO3 contributor Ralf Zimmermann who fixed the issue.

### References
* [TYPO3-CORE-SA-2021-002](https://typo3.org/security/advisory/typo3-core-sa-2021-002)

## References
- https://github.com/TYPO3/TYPO3.CMS/security/advisories/GHSA-2r6j-862c-m2v2
- https://nvd.nist.gov/vuln/detail/CVE-2021-21355
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms-core/CVE-2021-21355.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms/CVE-2021-21355.yaml
- https://packagist.org/packages/typo3/cms-form
- https://typo3.org/security/advisory/typo3-core-sa-2021-002
