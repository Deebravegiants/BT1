# [H] Akeneo PIM Community Edition vulnerable to remote php code execution

## Summary
Severity: High
Advisory: GHSA-w9wc-4xcq-8gr6
CVE: CVE-2022-46157
CWE: CWE-434, CWE-94
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-12-09
Source: https://github.com/advisories/GHSA-w9wc-4xcq-8gr6
Type: github-advisory

## Affected
- Packagist: `akeneo/pim-community-dev` — affected >=6.0.0 <6.0.53
- Packagist: `akeneo/pim-community-dev` — affected >=0 <5.0.119

## Details
### Impact
Akeneo PIM Community Edition versions before v5.0.119 and v6.0.53 allows remote authenticated users to execute arbitrary PHP code on the server by uploading a crafted image.


### Patches

Akeneo PIM Community Edition after the versions aforementioned provides patched Apache HTTP server configuration file, for docker setup and in documentation sample, to fix this vulnerability.  
Community Edition users must change their Apache HTTP server configuration accordingly to be protected.
The patch for Cloud Based Akeneo PIM Services customers has been applied since 30th October 2022. 

### Workarounds

Replace any reference to `<FilesMatch \.php$>` in your apache httpd configurations with: `<Location "/index.php">`, as shown in https://github.com/akeneo/pim-community-dev/blob/b4d79bb073c8b68ea26ab227c97cc78d86c4cba1/docker/httpd.conf#L39.

<!--
### References
_Are there any links users can visit to find out more?_


### For more information
 If you have any questions or comments about this advisory:
* Open an issue in [example link to repo](http://example.com)
* Email us at [example email address](mailto:example@example.com)
-->

## References
- https://github.com/akeneo/pim-community-dev/security/advisories/GHSA-w9wc-4xcq-8gr6
- https://nvd.nist.gov/vuln/detail/CVE-2022-46157
- https://github.com/akeneo/pim-community-dev/commit/891a2f70a9a200f199de06fe64d376d03787a81a
- https://github.com/akeneo/pim-community-dev
- https://github.com/akeneo/pim-community-dev/blob/b4d79bb073c8b68ea26ab227c97cc78d86c4cba1/docker/httpd.conf#L39
