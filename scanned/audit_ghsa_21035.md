# [C] VNCAuthProxy authentication bypass vulnerability

## Summary
Severity: Critical
Advisory: GHSA-237r-mx84-7x8c
CVE: CVE-2022-36436
CWE: CWE-287
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-09-16
Source: https://github.com/advisories/GHSA-237r-mx84-7x8c
Type: github-advisory

## Affected
- PyPI: `vncauthproxy` — affected >=0 <1.2.0

## Details
OSU Open Source Lab VNCAuthProxy through 1.1.1 is affected by an vncap/vnc/protocol.py VNCServerAuthenticator authentication-bypass vulnerability that could allow a malicious actor to gain unauthorized access to a VNC session or to disconnect a legitimate user from a VNC session. A remote attacker with network access to the proxy server could leverage this vulnerability to connect to VNC servers protected by the proxy server without providing any authentication credentials. Exploitation of this issue requires that the proxy server is currently accepting connections for the target VNC server.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-36436
- https://github.com/osuosl/twisted_vncauthproxy/commit/edc149af29242178091b2d6fcd42c3ef0851644b
- https://cert.grnet.gr/en/blog/cve-2022-36436-twisted-vnc-authentication-proxy-authentication-bypass
- https://github.com/osuosl/twisted_vncauthproxy
- https://github.com/osuosl/twisted_vncauthproxy/tree/release/1.1.1
- https://github.com/pypa/advisory-database/tree/main/vulns/vncauthproxy/PYSEC-2022-267.yaml
- https://pypi.org/project/VNCAuthProxy
