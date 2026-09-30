# [C] Remote code execution in zendframework and laminas-http

## Summary
Severity: Critical
Advisory: GHSA-xx8f-qf9f-5fgw
CVE: CVE-2021-3007
CWE: CWE-502
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-06-08
Source: https://github.com/advisories/GHSA-xx8f-qf9f-5fgw
Type: github-advisory

## Affected
- Packagist: `zendframework/zendframework` — affected >=0
- Packagist: `laminas/laminas-http` — affected >=0 <2.14.2

## Details
Laminas Project laminas-http before 2.14.2, and Zend Framework 3.0.0, has a deserialization vulnerability that can lead to remote code execution if the content is controllable, related to the __destruct method of the Zend\Http\Response\Stream class in Stream.php. NOTE: Zend Framework is no longer supported by the maintainer. NOTE: the laminas-http vendor considers this a "vulnerability in the PHP language itself" but has added certain type checking as a way to prevent exploitation in (unrecommended) use cases where attacker-supplied data can be deserialized.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-3007
- https://github.com/laminas/laminas-http/pull/48
- https://github.com/Ling-Yizhou/zendframework3-/blob/main/zend%20framework3%20%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96%20rce.md
- https://github.com/laminas/laminas-http/commits/2.15.x/src/Response/Stream.php
- https://github.com/laminas/laminas-http/releases/tag/2.14.2
- https://research.checkpoint.com/2021/freakout-leveraging-newest-vulnerabilities-for-creating-a-botnet
