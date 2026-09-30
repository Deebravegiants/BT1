# [M] Validator.isValidSafeHTML is being deprecated and will be deleted from org.owasp.esapi:esapi in 1 year

## Summary
Severity: Medium
Advisory: GHSA-r68h-jhhj-9jvm
Ecosystem: Maven
Published: 2023-11-27
Source: https://github.com/advisories/GHSA-r68h-jhhj-9jvm
Type: github-advisory

## Affected
- Maven: `org.owasp.esapi:esapi` — affected >=0 <2.6.0.0

## Details
### Impact
The `Validator.isValidSafeHTML` method can result in false negatives where it reports some input as safe (i.e., returns true), but really isn't, and using that same input as-is can in certain circumstances result in XSS vulnerabilities. Because this method cannot be fixed, it is being deprecated and will be removed in one years time from when this advisory is published. Full details may be found in [ESAPI Security Bulletin #12](https://github.com/ESAPI/esapi-java-legacy/blob/develop/documentation/ESAPI-security-bulletin12.pdf).

Note that all versions of ESAPI, that have this method (which dates back to at least the ESAPI 1.3 release more than 15 years ago) have this issue and it will continue to exist until we remove these two methods in a future ESAPI release.

### Patches
There is no patch. We do not believe that it is possible to patch this pretentiously named method other then perhaps renaming it to something like Validator.mightThisBeValidSafeHTML to dissuade developers from using it.

### Workarounds
Stop using this method. Note that `Validator.getValidSafeHTML` is believed to be safe to use with the default **antisamy-esapi.xml** AntiSamy policy file.

### Why is no CVE being filed?
We outline the reasons in the section "Why no CVE for this issue?" in [ESAPI Security Bulletin #12](https://github.com/ESAPI/esapi-java-legacy/blob/develop/documentation/ESAPI-security-bulletin12.pdf). If after reading that, if _you_ still want to file a CVE or this, knock yourself out.

### References
[CWE-79](https://cwe.mitre.org/data/definitions/79.html)
[CWE-80](https://cwe.mitre.org/data/definitions/80.html)
[ESAPI Security Bulletin #12](https://github.com/ESAPI/esapi-java-legacy/blob/develop/documentation/ESAPI-security-bulletin12.pdf)

### Final resolution
This GitHub Security Advisory should now be considered remediated in [ESAPI versions 2.6.0.0](https://github.com/ESAPI/esapi-java-legacy/releases/tag/esapi-2.6.0.0) and later as the deprecated methods have been removed from the ESAPI jar.

## References
- https://github.com/ESAPI/esapi-java-legacy/security/advisories/GHSA-r68h-jhhj-9jvm
- https://github.com/ESAPI/esapi-java-legacy
