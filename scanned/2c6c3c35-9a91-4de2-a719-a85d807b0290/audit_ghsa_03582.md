# [H] Cross-site scripting in eZ Platform Kernel

## Summary
Severity: High
Advisory: GHSA-mrvj-7q4f-5p42
CVE: CVE-2021-46875
CWE: CWE-79
Ecosystem: Packagist
Published: 2021-03-19
Source: https://github.com/advisories/GHSA-mrvj-7q4f-5p42
Type: github-advisory

## Affected
- Packagist: `ezsystems/ezpublish-kernel` — affected >=0 <6.13.8.2
- Packagist: `ezsystems/ezpublish-kernel` — affected >=7.0.0 <7.5.15.2
- Packagist: `ezsystems/ezplatform-kernel` — affected >=0 <1.2.5.1
- Packagist: `ezsystems/ezplatform-kernel` — affected >=1.3.0 <1.3.1.1

## Details
### Impact
In file upload it is possible by certain means to upload files like .html and .js. These may contain XSS exploits which will be run when links to them are accessed by victims.

### Patches
The fix consists simply of adding common types of scriptable file types to the configuration of the already existing filetype blacklist feature. See "Patched versions". As such, this can also be done manually, without installing the patched versions. This may be relevant if you are currently running a considerably older version of the kernel package and don't want to upgrade it at this time. Please see the settting "ezsettings.default.io.file_storage.file_type_blacklist" at:
https://github.com/ezsystems/ezplatform-kernel/blob/master/eZ/Bundle/EzPublishCoreBundle/Resources/config/default_settings.yml#L109

### Important note
You should adapt this setting to your needs. Do not add file types to the blacklist that you actually need to be able to upload. For instance, if you need your editors to be able to upload SVG files, then don't blacklist that. Instead, you could e.g. use an approval workflow for such content.

## References
- https://github.com/ezsystems/ezpublish-kernel/security/advisories/GHSA-mrvj-7q4f-5p42
- https://nvd.nist.gov/vuln/detail/CVE-2021-46875
- https://github.com/ezsystems/ezpublish-kernel/commit/29fecd2afe86f763510f10c02f14962d028f311b
- https://github.com/ezsystems/ezpublish-kernel
- https://packagist.org/packages/ezsystems/ezplatform-kernel#v1.2.5.1
- https://packagist.org/packages/ezsystems/ezpublish-kernel#v7.5.15.2
