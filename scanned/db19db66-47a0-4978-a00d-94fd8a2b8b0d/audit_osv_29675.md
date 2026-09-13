# [M] Apache Druid: Padding oracle in druid-pac4j extension that allows an attacker to manipulate a pac4j session cookie via Padding Oracle Attack

## Summary
Severity: Medium
Advisory: CVE-2024-45384
Aliases: GHSA-p72w-r6fv-6g5h
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2024-09-17
Source: https://osv.dev/vulnerability/CVE-2024-45384
Type: osv

## Details
Padding Oracle vulnerability in Apache Druid extension, druid-pac4j.
This could allow an attacker to manipulate a pac4j session cookie.

This issue affects Apache Druid versions 0.18.0 through 30.0.0.
Since the druid-pac4j extension is optional and disabled by default, Druid installations not using the druid-pac4j extension are not affected by this vulnerability.

While we are not aware of a way to meaningfully exploit this flaw, we 
nevertheless recommend upgrading to version 30.0.1 or higher which fixes the issue
and ensuring you have a strong 
druid.auth.pac4j.cookiePassphrase as a precaution.

## References
- http://www.openwall.com/lists/oss-security/2024/09/17/1
- https://repo.maven.apache.org/maven2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/45xxx/CVE-2024-45384.json
- https://lists.apache.org/thread/gr94fnp574plb50lsp8jw4smvgv1lbz1
- https://nvd.nist.gov/vuln/detail/CVE-2024-45384
