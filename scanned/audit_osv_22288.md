# [H] Uncontrolled Resource Consumption in org.cyberneko.html (nokogiri fork)

## Summary
Severity: High
Advisory: CVE-2022-24839
Aliases: GHSA-9849-p7jc-9rmv
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-04-11
Source: https://osv.dev/vulnerability/CVE-2022-24839
Type: osv

## Details
org.cyberneko.html is an html parser written in Java. The fork of `org.cyberneko.html` used by Nokogiri (Rubygem) raises a `java.lang.OutOfMemoryError` exception when parsing ill-formed HTML markup. Users are advised to upgrade to `>= 1.9.22.noko2`. Note: The upstream library `org.cyberneko.html` is no longer maintained. Nokogiri uses its own fork of this library located at https://github.com/sparklemotion/nekohtml and this CVE applies only to that fork. Other forks of nekohtml may have a similar vulnerability.

## References
- https://www.oracle.com/security-alerts/cpujul2022.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/24xxx/CVE-2022-24839.json
- https://github.com/sparklemotion/nekohtml/security/advisories/GHSA-9849-p7jc-9rmv
- https://nvd.nist.gov/vuln/detail/CVE-2022-24839
- https://github.com/sparklemotion/nekohtml/commit/a800fce3b079def130ed42a408ff1d09f89e773d
