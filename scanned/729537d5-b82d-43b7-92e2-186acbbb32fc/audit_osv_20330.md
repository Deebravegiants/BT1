# [C] CVE-2021-32802

## Summary
Severity: Critical
Advisory: CVE-2021-32802
Aliases: GHSA-m682-v4g9-wrq7
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-09-07
Source: https://osv.dev/vulnerability/CVE-2021-32802
Type: osv

## Details
Nextcloud server is an open source, self hosted personal cloud. Nextcloud supports rendering image previews for user provided file content. For some image types, the Nextcloud server was invoking a third-party library that wasn't suited for untrusted user-supplied content. There are several security concerns with passing user-generated content to this library, such as Server-Side-Request-Forgery, file disclosure or potentially executing code on the system. The risk depends on your system configuration and the installed library version. It is recommended that the Nextcloud Server is upgraded to 20.0.12, 21.0.4 or 22.1.0. These versions do not use this library anymore. As a workaround users may disable previews by setting `enable_previews` to `false` in `config.php`.

## References
- https://docs.nextcloud.com/server/21/admin_manual/configuration_files/previews_configuration.html#disabling-previews
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-m682-v4g9-wrq7
- https://security.gentoo.org/glsa/202208-17
- https://hackerone.com/reports/1261413
