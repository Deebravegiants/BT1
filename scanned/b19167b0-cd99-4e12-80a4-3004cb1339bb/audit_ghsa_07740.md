# [M] Indico has Server-Side Request Forgery (SSRF) in multiple places

## Summary
Severity: Medium
Advisory: GHSA-f47c-3c5w-v7p4
CVE: CVE-2026-25738
CWE: CWE-367, CWE-918
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2026-02-17
Source: https://github.com/advisories/GHSA-f47c-3c5w-v7p4
Type: github-advisory

## Affected
- PyPI: `indico` — affected >=0 <3.3.10

## Details
### Impact
Indico makes outgoing requests to user-provides URLs in various places. This is mostly intentional and part of Indico's functionality, but of course it is never intended to let you access "special" targets such as localhost or cloud metadata endpoints.

### Patches
You should to update to [Indico 3.3.10](https://github.com/indico/indico/releases/tag/v3.3.10) as soon as possible.
See [the docs](https://docs.getindico.io/en/stable/installation/upgrade/) for instructions on how to update.

### Workarounds
If you do not have IPs that expose sensitive data without authentication (typically because you do not host Indico on AWS), this vulnerability doesn't impact you and you can ignore it (but please upgrade anyway).
Also, only event organizers can access endpoints where SSRF could be used to actually see the data returned by such a request. So if you trust your event organizers, the risk is also very limited.

For additional security, both before and after patching, you could also use the common proxy-related environment variables (in particular `http_proxy` and `https_proxy`) to force outgoing requests to go through a proxy that limits requests in whatever way you deem useful/necessary. These environment variables would need to be set both on the indico-uwsgi and indico-celery services. Please note that setting up such a proxy is not something we can help you with.

### For more information
If you have any questions or comments about this advisory:

- Open a thread in [our forum](https://talk.getindico.io/)
- Email us privately at [indico-team@cern.ch](mailto:indico-team@cern.ch)

## References
- https://github.com/indico/indico/security/advisories/GHSA-f47c-3c5w-v7p4
- https://nvd.nist.gov/vuln/detail/CVE-2026-25738
- https://github.com/indico/indico/commit/70d341826116fac5868719a6133f2c26d9345137
- https://github.com/indico/indico
- https://github.com/indico/indico/releases/tag/v3.3.10
