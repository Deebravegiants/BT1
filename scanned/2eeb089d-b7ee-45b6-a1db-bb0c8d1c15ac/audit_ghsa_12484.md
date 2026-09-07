# [M] User accounts disclosed to unauthenticated actors on the LAN

## Summary
Severity: Medium
Advisory: GHSA-jqpc-rc7g-vf83
CVE: CVE-2023-50715
CWE: CWE-200
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2023-12-15
Source: https://github.com/advisories/GHSA-jqpc-rc7g-vf83
Type: github-advisory

## Affected
- PyPI: `homeassistant` — affected >=0 <2023.12.3

## Details
### Summary

The login page discloses all active user accounts to any unauthenticated browsing request originating on the Local Area Network.

### Details

Starting the [Home Assistant 2023.12 release](https://www.home-assistant.io/blog/2023/12/06/release-202312/), the login page returns all currently active user accounts to browsing requests from the Local Area Network. Tests showed that this occurs when:

- The request is not authenticated and
- The request originated locally, meaning on the Home Assistant host local subnet or any other private subnet (`10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16, fd00::/8, ::ffff:10.0.0.0/104, ::ffff:172.16.0.0/108, ::ffff:192.168.0.0/112`)

The rationale behind this is to make the login more user-friendly (see [release blog post](https://www.home-assistant.io/blog/2023/12/06/release-202312/)) and an experience better aligned with other applications that have multiple user-profiles.

However, as a result, all accounts are displayed regardless of them having logged in or not and for any device that navigates to the server. This disclosure is mitigated by the fact that it only occurs for requests originating from a LAN address. But note that this applies to the local subnet where Home Assistant resides and to any private subnet that can reach it.

### PoC

1. Place a Home Assistant instance on a private subnet, i.e., 192.168.1.0/24.
2. Create a few users, let's say, three.
3. From any (or another) private subnet on the LAN, like 192.168.2.0/24, open an incognito browser window (to ensure that the browser has no cookies from Home Assistant and therefore is demonstrably unauthenticated) and navigate to the Home Assistant URL.
4. The login page will display all three users, including their profile photo.

### Impact

The following CVSS string could be shaped to describe the overall impact of this issue:
AV:A/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N

As seen, the Exploitability metrics are high, and the Impact metrics are low. This is fitting because the problem does not constitute a critical one, but at the same time, it is trivial to exploit. Still, since the mitigation can be so easily implemented in code to eliminate a typical case of information disclosure, it would certainly be worth pursuing.

## References
- https://github.com/home-assistant/core/security/advisories/GHSA-jqpc-rc7g-vf83
- https://nvd.nist.gov/vuln/detail/CVE-2023-50715
- https://github.com/home-assistant/core/commit/dbfc5ea8f96bde6cd165892f5a6a6f9a65731c76
- https://github.com/home-assistant/core
