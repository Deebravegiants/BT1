# [C] CVE-2021-21425

## Summary
Severity: Critical
Advisory: CVE-2021-21425
Aliases: GHSA-6f53-6qgv-39pj
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-04-07
Source: https://osv.dev/vulnerability/CVE-2021-21425
Type: osv

## Details
Grav Admin Plugin is an HTML user interface that provides a way to configure Grav and create and modify pages. In versions 1.10.7 and earlier, an unauthenticated user can execute some methods of administrator controller without needing any credentials. Particular method execution will result in arbitrary YAML file creation or content change of existing YAML files on the system. Successfully exploitation of that vulnerability results in configuration changes, such as general site information change, custom scheduler job definition, etc. Due to the nature of the vulnerability, an adversary can change some part of the webpage, or hijack an administrator account, or execute operating system command under the context of the web-server user. This vulnerability is fixed in version 1.10.8. Blocking access to the `/admin` path from untrusted sources can be applied as a workaround.

## References
- http://packetstormsecurity.com/files/162283/GravCMS-1.10.7-Remote-Command-Execution.html
- http://packetstormsecurity.com/files/162457/GravCMS-1.10.7-Remote-Command-Execution.html
- https://github.com/getgrav/grav-plugin-admin/security/advisories/GHSA-6f53-6qgv-39pj
- https://pentest.blog/unexpected-journey-7-gravcms-unauthenticated-arbitrary-yaml-write-update-leads-to-code-execution/
