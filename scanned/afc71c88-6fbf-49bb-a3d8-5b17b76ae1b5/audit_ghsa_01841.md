# [C] Apache Log4j Remote Code Execution

## Summary
Severity: Critical
Advisory: GHSA-mf4f-j588-5xm8
Ecosystem: Maven
Published: 2021-12-14
Source: https://github.com/advisories/GHSA-mf4f-j588-5xm8
Type: github-advisory

## Affected
- Maven: `org.opencastproject:opencast-common` — affected >=0 <9.10
- Maven: `org.opencastproject:opencast-common` — affected >=10.0 <10.6

## Details
### Impact

Opencast uses an Apache Log4j2 version which, combined with older JDK versions, can be used for remote code execution attacks which have been found to be actively exploited.

Apache Log4j2 <=2.14.1 JNDI features is not sufficiently protected. An attacker who can control log messages or log message parameters can execute arbitrary code when message lookup substitution is enabled.

### Who is affected

- Opencast before 9.10 or 10.6 are affected
    - Log4j version: all 2.x versions before 2.15.0 are affected

### Patches

The issue has been fixed in Opencast 9.10 and 10.6.

### Workarounds

The vulnerability can be mitigated by setting system property `log4j2.formatMsgNoLookups` to `true`.

### References

- [Opencast pull request mitigating the vulnerability](https://github.com/opencast/opencast/pull/3253)
- [CVE-2021-44228 Detail](https://nvd.nist.gov/vuln/detail/CVE-2021-44228)
- [Analysis and Remediation Guidance to the Log4j Zero-Day RCE (CVE-2021-44228) Vulnerability](https://www.veracode.com/blog/security-news/urgent-analysis-and-remediation-guidance-log4j-zero-day-rce-cve-2021-44228)
- [VE-2021-44228 – Log4j 2 Vulnerability Analysis](https://www.randori.com/blog/cve-2021-44228/)

### For more information

If you have any questions or comments about this advisory:
* Open an issue in [our issue tracker](https://github.com/opencast/opencast/issues)
* Email us at [security@opencast.org](mailto:security@opencast.org)


### Note about dependencies

This issue affects many Java applications. Please also verify these are not vulnerable.

## References
- https://github.com/opencast/opencast/security/advisories/GHSA-mf4f-j588-5xm8
- https://nvd.nist.gov/vuln/detail/CVE-2021-44228
- https://github.com/opencast/opencast/pull/3253
- https://docs.opencast.org/r/10.x/admin/#changelog/#opencast-106
- https://docs.opencast.org/r/9.x/admin/#changelog/#opencast-910
- https://github.com/opencast/opencast
