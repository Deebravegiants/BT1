# [M] icingaweb2-module-incubator base implementation for HTML forms is susceptible to CSRF

## Summary
Severity: Medium
Advisory: CVE-2024-24819
Aliases: GHSA-p8vv-9pqq-rm8p
CVSS: 5.3 (CVSS:3.1/AV:N/AC:H/PR:H/UI:R/S:U/C:L/I:H/A:L)
Published: 2024-02-09
Source: https://osv.dev/vulnerability/CVE-2024-24819
Type: osv

## Details
icingaweb2-module-incubator is a working project of bleeding edge Icinga Web 2 libraries. In affected versions the class `gipfl\Web\Form` is the base for various concrete form implementations [1] and provides protection against cross site request forgery (CSRF) by default. This is done by automatically adding an element with a CSRF token to any form, unless explicitly disabled, but even if enabled, the CSRF token (sent during a client's submission of a form relying on it) is not validated. This enables attackers to perform changes on behalf of a user which, unknowingly, interacts with a prepared link or website. The version 0.22.0 is available to remedy this issue. Users are advised to upgrade. There are no known workarounds for this vulnerability.

## References
- https://github.com/search?q=gipfl%5CWeb%5CForm%3B&type=code
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/24xxx/CVE-2024-24819.json
- https://github.com/Icinga/icingaweb2-module-incubator/security/advisories/GHSA-p8vv-9pqq-rm8p
- https://nvd.nist.gov/vuln/detail/CVE-2024-24819
- https://github.com/Icinga/icingaweb2-module-incubator/commit/db7dc49585fee0b4e96be666d7f6009a74a1ccb5
