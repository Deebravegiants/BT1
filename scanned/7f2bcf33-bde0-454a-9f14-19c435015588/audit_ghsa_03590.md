# [H] Sensitive information disclosure via log in com.bmuschko:gradle-vagrant-plugin

## Summary
Severity: High
Advisory: GHSA-jpcm-4485-69p7
CVE: CVE-2021-21361
CWE: CWE-532
Ecosystem: Maven
CVSS: CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2021-03-09
Source: https://github.com/advisories/GHSA-jpcm-4485-69p7
Type: github-advisory

## Affected
- Maven: `com.bmuschko:gradle-vagrant-plugin` — affected >=0.6 <3.0.0

## Details
### Impact

The `com.bmuschko:gradle-vagrant-plugin` Gradle plugin contains an information disclosure vulnerability due to the logging of the system environment variables.

When this Gradle plugin is executed in public CI/CD, this can lead to sensitive credentials being exposed to malicious actors.

### Patches
Fixed in version 3.0.0

### References

 - https://github.com/bmuschko/gradle-vagrant-plugin/blob/292129f9343d00d391543fae06239e9b0f33db73/src/main/groovy/com/bmuschko/gradle/vagrant/process/GDKExternalProcessExecutor.groovy#L42-L44
 - https://github.com/bmuschko/gradle-vagrant-plugin/issues/19
 - https://github.com/bmuschko/gradle-vagrant-plugin/pull/20

### For more information

If you have any questions or comments about this advisory:
* Open an issue in [bmuschko/gradle-vagrant-plugin](https://github.com/bmuschko/gradle-vagrant-plugin)

## References
- https://github.com/JLLeitschuh/security-research/security/advisories/GHSA-jpcm-4485-69p7
- https://nvd.nist.gov/vuln/detail/CVE-2021-21361
- https://github.com/bmuschko/gradle-vagrant-plugin/issues/19
- https://github.com/bmuschko/gradle-vagrant-plugin/pull/20
- https://github.com/bmuschko/gradle-vagrant-plugin/blob/292129f9343d00d391543fae06239e9b0f33db73/src/main/groovy/com/bmuschko/gradle/vagrant/process/GDKExternalProcessExecutor.groovy#L42-L44
