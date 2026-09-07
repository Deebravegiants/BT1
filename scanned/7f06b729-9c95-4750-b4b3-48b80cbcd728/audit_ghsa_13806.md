# [H] Reactor Netty HTTP Server denial of service vulnerability

## Summary
Severity: High
Advisory: GHSA-q24v-hpg3-v3jp
CVE: CVE-2023-34054
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-11-28
Source: https://github.com/advisories/GHSA-q24v-hpg3-v3jp
Type: github-advisory

## Affected
- Maven: `io.projectreactor.netty:reactor-netty-core` — affected >=1.1.0 <1.1.13
- Maven: `io.projectreactor.netty:reactor-netty-core` — affected >=1.0.0 <1.0.39

## Details
In Reactor Netty HTTP Server, versions 1.1.x prior to 1.1.13 and versions 1.0.x prior to 1.0.39, it is possible for a user to provide specially crafted HTTP requests that may cause a denial-of-service (DoS) condition.

Specifically, an application is vulnerable if Reactor Netty HTTP Server built-in integration with Micrometer is enabled.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-34054
- https://github.com/reactor/reactor-netty/commit/37dc8a2ef6514cd7834e75e7f3faf0b9ea044c88
- https://github.com/reactor/reactor-netty/commit/4ddbb1b9b985bb72290110ebae468a54e7f19420
- https://github.com/reactor/reactor-netty/commit/ae82154e99e6f51f4816effd135f0c3a966d6ea3
- https://github.com/reactor/reactor-netty
- https://github.com/reactor/reactor-netty/releases/tag/v1.0.39
- https://github.com/reactor/reactor-netty/releases/tag/v1.1.13
- https://spring.io/security/cve-2023-34054
