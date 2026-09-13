# [H] graphite.composer.views.send_email vulnerable to SSRF

## Summary
Severity: High
Advisory: GHSA-vfj6-275q-4pvm
CVE: CVE-2017-18638
CWE: CWE-918
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2019-10-25
Source: https://github.com/advisories/GHSA-vfj6-275q-4pvm
Type: github-advisory

## Affected
- PyPI: `graphite-web` — affected >=0 <1.1.6

## Details
### Impact
send_email in graphite-web/webapp/graphite/composer/views.py in Graphite through 1.1.5 is vulnerable to SSRF. The vulnerable SSRF endpoint can be used by an attacker to have the Graphite web server request any resource. The response to this SSRF request is encoded into an image file and then sent to an e-mail address that can be supplied by the attacker. Thus, an attacker can exfiltrate any information. Email will be send through SMTP server configured in Graphite, by default it's 'localhost'

### Patches
Problem was patched in Graphite-web 1.1.6. Also patches was released for graphite-web [1.0.x](https://github.com/graphite-project/graphite-web/pull/2501) and [0.9.x](https://github.com/graphite-project/graphite-web/pull/2500), and we'll discuss releases of non-supported branches later.

### Workarounds
You can manually remove function `send_email` from file `webapp/graphite/composer/views.py`. This function are not in use and will not affect your Graphite installation.

### References
For more information check this graphite-web Github issue #2008 

### For more information
If you have any questions or comments about this advisory:
* Add comment in [issue #2008](https://github.com/graphite-project/graphite-web/issues/2008)

## References
- https://github.com/graphite-project/graphite-web/security/advisories/GHSA-vfj6-275q-4pvm
- https://nvd.nist.gov/vuln/detail/CVE-2017-18638
- https://github.com/graphite-project/graphite-web/issues/2008
- https://github.com/graphite-project/graphite-web/pull/2499
- https://github.com/graphite-project/graphite-web/commit/71726a0e41a5263f49b973a7b856505a5b931c1f
- https://blog.orange.tw/2017/07/how-i-chained-4-vulnerabilities-on.html#second-bug-internal-graphite-ssrf
- https://github.com/graphite-project/graphite-web
- https://github.com/pypa/advisory-database/tree/main/vulns/graphite-web/PYSEC-2019-151.yaml
- https://lists.debian.org/debian-lts-announce/2019/10/msg00030.html
- https://www.youtube.com/watch?v=ds4Gp4xoaeA
