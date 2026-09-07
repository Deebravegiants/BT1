# [M] actionpack Open Redirect in Host Authorization Middleware

## Summary
Severity: Medium
Advisory: GHSA-qphc-hf5q-v8fc
CVE: CVE-2021-44528
CWE: CWE-601
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2021-12-14
Source: https://github.com/advisories/GHSA-qphc-hf5q-v8fc
Type: github-advisory

## Affected
- RubyGems: `actionpack` — affected >=6.0.0 <6.0.4.2
- RubyGems: `actionpack` — affected >=6.1.0 <6.1.4.2

## Details
Specially crafted "X-Forwarded-Host" headers in combination with certain "allowed host" formats can cause the Host Authorization middleware in Action Pack to redirect users to a malicious website.

Impacted applications will have allowed hosts with a leading dot. For example, configuration files that look like this:

```
config.hosts <<  '.EXAMPLE.com'
```

When an allowed host contains a leading dot, a specially crafted Host header can be used to redirect to a malicious website.

This vulnerability is similar to CVE-2021-22881 and CVE-2021-22942.

Releases
--------
The fixed releases are available at the normal locations.

Patches
-------
To aid users who aren't able to upgrade immediately we have provided patches for the two supported release series. They are in git-am format and consist of a single changeset.

* 6-0-host-authorzation-open-redirect.patch - Patch for 6.0 series
* 6-1-host-authorzation-open-redirect.patch - Patch for 6.1 series
* 7-0-host-authorzation-open-redirect.patch - Patch for 7.0 series

Please note that only the 6.1.Z, 6.0.Z, and 5.2.Z series are supported at present. Users of earlier unsupported releases are advised to upgrade as soon as possible as we cannot guarantee the continued availability of security fixes for unsupported releases.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-44528
- https://github.com/rails/rails/commit/0fccfb9a3097a9c4260c791f1a40b128517e7815
- https://github.com/rails/rails/commit/aecba3c301b80e9d5a63c30ea1b287bceaf2c107
- https://github.com/rails/rails
- https://github.com/rails/rails/blob/v6.1.4.2/actionpack/CHANGELOG.md#rails-6142-december-14-2021
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/actionpack/CVE-2021-44528.yml
- https://groups.google.com/g/ruby-security-ann/c/vG9gz3nk1pM/m/7-NU4MNrDAAJ
- https://groups.google.com/g/ruby-security-ann/c/vG9gz3nk1pM/m/7-NU4MNrDAAJ?utm_medium=email&utm_source=footer
- https://security.netapp.com/advisory/ntap-20240208-0003
- https://www.debian.org/security/2023/dsa-5372
