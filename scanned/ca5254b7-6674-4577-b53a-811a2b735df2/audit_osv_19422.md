# [H] CVE-2021-21265

## Summary
Severity: High
Advisory: CVE-2021-21265
Aliases: GHSA-xhfx-hgmf-v6vp
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2021-03-10
Source: https://osv.dev/vulnerability/CVE-2021-21265
Type: osv

## Details
October is a free, open-source, self-hosted CMS platform based on the Laravel PHP Framework. In October before version 1.1.2, when running on poorly configured servers (i.e. the server routes any request, regardless of the HOST header to an October CMS instance) the potential exists for Host Header Poisoning attacks to succeed. This has been addressed in version 1.1.2 by adding a feature to allow a set of trusted hosts to be specified in the application. As a workaround one may set the configuration setting cms.linkPolicy to force.

## References
- https://packagist.org/packages/october/backend
- https://github.com/octobercms/library/commit/f29865ae3db7a03be7c49294cd93980ec457f10d
- https://github.com/octobercms/library/commit/f86fcbcd066d6f8b939e8fe897409d152b11c3c6
- https://github.com/octobercms/october/commit/555ab61f2313f45d7d5d138656420ead536c5d30
- https://github.com/octobercms/october/commit/f638d3f78cfe91d7f6658820f9d5e424306a3db0
- https://github.com/octobercms/october/security/advisories/GHSA-xhfx-hgmf-v6vp
