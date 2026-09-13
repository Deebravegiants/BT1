# [H] Kirby: Access to image files and limited access to JSON files outside of the site root via path traversal in the media handling

## Summary
Severity: High
Advisory: GHSA-9vx2-j98c-p72w
CVE: CVE-2026-75594
CWE: CWE-22
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-08-31
Source: https://github.com/advisories/GHSA-9vx2-j98c-p72w
Type: github-advisory

## Affected
- Packagist: `getkirby/cms` — affected >=0 <4.9.5
- Packagist: `getkirby/cms` — affected >=5.0.0 <5.5.2

## Details
### TL;DR

This vulnerability affects all Kirby sites that are deployed to a server that allows requests for URLs with encoded slashes (`%2f`), such as nginx, PHP's built-in server or Apache setups that have the option `AllowEncodedSlashes` enabled.
 
It was possible to create and access thumbnails from media files in arbitrary accessible directories on the server that have a valid thumbnail configuration (JSON job file). It was also possible to detect the presence of files with the `.json` file extension anywhere on the server.
 
**This vulnerability is of high severity for affected sites.**
 
Server setups using Apache's default configuration or other servers that have been hardened against encoded slashes in URLs are *not* affected.

----

### Introduction

A path traversal (also known as directory traversal) vulnerability occurs when untrusted input is used to build a filesystem path without properly confining the result to an intended base directory. By injecting sequences such as `../`, an attacker can escape that directory and reach files elsewhere on the server.

### Affected components

Kirby's media handler processes requests for files in the `media` directory that have not been generated yet. It parses the provided path and finds the correct file or asset from which to generate a thumbnail. Each thumbnail needs to have a prepared job file (a metadata file with file extension `.json`) in order to allow the media handler to generate it.
 
Each parent (such as a page) has its own media directory, which in turn contains the individual files. Kirby's media handler searches for the file within the parent's media directory.

### Impact

In affected releases, Kirby did not prevent path traversal in the filenames that were searched within the parent directory. In affected server setups where the attacker can provide encoded slashes (`%2f`) in the request, Kirby allowed the request to traverse away from the parent's media directory.
 
Because the response differs between existing and non-existing thumbnail configurations, attackers were able to tell whether an arbitrary JSON file exists on the server (addressed by a relative path from the media directory of an arbitrary existing parent, including a relative path that points outside of the site's `index` root). For existing files with the file extension `.json` and a valid `filename` key (resulting in a valid job file), it was possible to generate thumbnails of the referenced media files, deleting the job file in the process.
 
### Patches

The problem has been patched in [Kirby 4.9.5](https://github.com/getkirby/kirby/releases/tag/4.9.5) and [Kirby 5.5.2](https://github.com/getkirby/kirby/releases/tag/5.5.2). Please update to one of these or a [later version](https://github.com/getkirby/kirby/releases) to fix the vulnerability.

In all of the mentioned releases, `Kirby\Cms\Media::thumb()` now rejects any filename that contains path information (anything other than a plain filename) before it is appended to the validated root. We have also hardened the `file::version` component to block paths that contain the `../` sequence.

### Credits

Thanks to Jorge González Milla (@Pig-Tail) for responsibly reporting the identified issue.

## References
- https://github.com/getkirby/kirby/security/advisories/GHSA-9vx2-j98c-p72w
- https://nvd.nist.gov/vuln/detail/CVE-2026-75594
- https://github.com/getkirby/kirby/commit/22fbaedb7e6dd61f5def10829ba7bd7e73e0dcc9
- https://github.com/getkirby/kirby/commit/a40808f5c2ee5d42bb597fb6ffbe0de0ce8e4d20
- https://github.com/getkirby/kirby/commit/cd7abb68d298f3443eafd43fa2d0c7ad0f933d0e
- https://github.com/getkirby/kirby/commit/e0dca5f709adc21b36f5549df2c0619bc59da56c
- https://github.com/getkirby/kirby
- https://github.com/getkirby/kirby/releases/tag/4.9.5
- https://github.com/getkirby/kirby/releases/tag/5.5.2
