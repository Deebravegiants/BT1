# [H] Unauthenticated access to Ironic API

## Summary
Severity: High
Advisory: CVE-2023-40585
Aliases: GHSA-jwpr-9fwh-m4g7
CVSS: 7.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2023-08-25
Source: https://osv.dev/vulnerability/CVE-2023-40585
Type: osv

## Details
ironic-image is a container image to run OpenStack Ironic as part of Metal³. Prior to version capm3-v1.4.3, if Ironic is not deployed with TLS and it does not have API and Conductor split into separate services, access to the API is not protected by any authentication. Ironic API is also listening in host network. In case the node is not behind a firewall, the API could be accessed by anyone via network without authentication. By default, Ironic API in Metal3 is protected by TLS and basic authentication, so this vulnerability requires operator to configure API without TLS for it to be vulnerable. TLS and authentication however should not be coupled as they are in versions prior to capm3-v1.4.3. A patch exists in versions capm3-v1.4.3 and newer. Some workarounds are available. Either configure TLS for Ironic API (`deploy.sh -t ...`, `IRONIC_TLS_SETUP=true`) or split Ironic API and Conductor via configuration change (old implementation, not recommended). With both workarounds, services are configured with httpd front-end, which has proper authentication configuration in place.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/40xxx/CVE-2023-40585.json
- https://github.com/metal3-io/ironic-image/security/advisories/GHSA-jwpr-9fwh-m4g7
- https://nvd.nist.gov/vuln/detail/CVE-2023-40585
- https://github.com/metal3-io/ironic-image/commit/f64bb6ce0945bbfb30d9965f98149ea183311de9
