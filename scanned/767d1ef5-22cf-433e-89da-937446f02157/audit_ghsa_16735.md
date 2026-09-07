# [H] OctoPrint has an Authentication Bypass via X-Forwarded-For Header when autologinLocal is enabled

## Summary
Severity: High
Advisory: GHSA-2vjq-hg5w-5gm7
CVE: CVE-2024-32977
CWE: CWE-290
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:A/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2024-05-14
Source: https://github.com/advisories/GHSA-2vjq-hg5w-5gm7
Type: github-advisory

## Affected
- PyPI: `OctoPrint` — affected >=0 <1.10.1

## Details
### Impact

OctoPrint versions up until and including 1.10.0 contain a vulnerability that allows an unauthenticated attacker to completely bypass the authentication **if the `autologinLocal` option is enabled** within `config.yaml`, even if they come from networks that are not configured as `localNetworks`, by spoofing their IP via the `X-Forwarded-For` header.

If autologin is not enabled, this vulnerability does not have any impact.

### Patches

The vulnerability has been patched in version 1.10.1.

### Workaround

Until the patch has been applied, OctoPrint administrators who have autologin enabled on their instances should disable it and/or to make the instance inaccessible from potentially hostile networks like the internet.

### PoC

1. Enable the `autologinAs` configuration within the `accessControl` section in the [OctoPrint yaml configuration file](https://docs.octoprint.org/en/master/configuration/config_yaml.html#access-control)
2. Set your browser to add the `X-Forwarded-For: 127.0.0.1` header to HTTP requests. For example, this can be done using proxy software like Burp Suite. Alternatively, there are browser extensions such as https://github.com/MisterPhilip/x-forwarded-for, but I haven't tried them.
3. Navigate to OctoPrint and note that it logs you in automatically.

### Credits

This vulnerability was discovered and responsibly disclosed to OctoPrint by Jacopo Tediosi.

## References
- https://github.com/OctoPrint/OctoPrint/security/advisories/GHSA-2vjq-hg5w-5gm7
- https://nvd.nist.gov/vuln/detail/CVE-2024-32977
- https://github.com/OctoPrint/OctoPrint/commit/5afbec8d23508edc25b0f1bdef1620580136add4
- https://github.com/OctoPrint/OctoPrint
- https://github.com/pypa/advisory-database/tree/main/vulns/octoprint/PYSEC-2024-237.yaml
