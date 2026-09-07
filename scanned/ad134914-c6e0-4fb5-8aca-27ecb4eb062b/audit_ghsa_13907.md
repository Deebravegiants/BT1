# [M] wallabag contains Improper Authorization via export feature

## Summary
Severity: Medium
Advisory: GHSA-qwx8-mxxx-mg96
CVE: CVE-2023-0609
CWE: CWE-285
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-02-02
Source: https://github.com/advisories/GHSA-qwx8-mxxx-mg96
Type: github-advisory

## Affected
- Packagist: `wallabag/wallabag` — affected >=2.0.0-alpha.1 <2.5.3

## Details
# Description

The export feature lets a user export a single entry or a set of entries in a given format (_e.g. PDF, MOBI, TXT_).

For example, `https://yourinstance.wallabag.org/export/45.pdf` will export the entry with id 45 in PDF format.

Since wallabag 2.0.0-alpha.1, this feature is vulnerable to an insecure direct object reference attack. A logged user can export any single entry without ownership validation.

This is due to a lack of access validation in the `downloadEntryAction` method.

**You should immediately patch your instance to version 2.5.3 or higher if you have more than one user and/or having open registration.**

# Resolution

A user check is now done in the vulnerable method before sending the exported entry.

The `Entry` retrieval through a `ParamConverter` has also been replaced with a call to the `EntryRepository` in order to prevent any information disclosure through response discrepancy.

# Workaround

If you are unable to update to the latest version or if you want to temporarily limit risk of exploitation, you may consider blocking requests to the endpoint `/export/*`.

E.g. with nginx:

``` nginx
    location /export {
        deny all;
    }
```

# Credits

We would like to thank @bAuh0lz for reporting this issue through huntr.dev.

Reference: https://www.huntr.dev/bounties/3adef66f-fc86-4e6d-a540-2ffa59342ff0/

## References
- https://github.com/wallabag/wallabag/security/advisories/GHSA-qwx8-mxxx-mg96
- https://nvd.nist.gov/vuln/detail/CVE-2023-0609
- https://github.com/wallabag/wallabag/commit/0f7460dbab9e29f4f7d2944aca20210f828b6abb
- https://github.com/wallabag/wallabag
- https://huntr.dev/bounties/3adef66f-fc86-4e6d-a540-2ffa59342ff0
