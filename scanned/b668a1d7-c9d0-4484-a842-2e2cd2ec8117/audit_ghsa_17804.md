# [H] Updatecli exposes Maven credentials in console output

## Summary
Severity: High
Advisory: GHSA-v34r-vj4r-38j6
CVE: CVE-2025-24355
CWE: CWE-359
Ecosystem: Go
CVSS: CVSS:3.0/AV:L/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2025-01-24
Source: https://github.com/advisories/GHSA-v34r-vj4r-38j6
Type: github-advisory

## Affected
- Go: `github.com/updatecli/updatecli` — affected >=0 <0.93.0

## Details
### Summary

Private maven repository credentials leaked in application logs in case of unsuccessful retrieval operation.

### Details

During the execution of an updatecli pipeline which contains a `maven` source configured with basic auth credentials, the credentials are being leaked in the application execution logs in case of failure.

Credentials are properly sanitized when the operation is successful but not when for whatever reason there is a failure in the maven repository .e.g. wrong coordinates provided, not existing artifact or version.

### PoC

The [documentation](https://www.updatecli.io/docs/plugins/resource/maven/) currently state to provide user credentials as basic auth inside the `repository` field. e.g.

```
sources:
  default:
    kind: maven
    spec:
      repository: "{{ requiredEnv "MAVEN_USERNAME" }}:{{ requiredEnv "MAVEN_PASS" }}@repo.example.org/releases"
      groupid: "org.example.company"
      artifactid: "my-artifact"
      versionFilter:
        kind: regex
        pattern: "^23(\.[0-9]+){1,2}$"
```

Logs are sanitized properly in case of a successful operation:

```
source: source#default
-----------------------------------------------------------
Searching for version matching pattern "^23(\\.[0-9]+){1,2}$"
✔ Latest version is 23.4.0 on the Maven repository at https://repo.example.org/releases/org/example/company/my-artifact/maven-metadata.xml
```

but leaks credentials in case the GAV coordinates are wrong (misspelled package name or missing):

```
source: source#default
-----------------------------------------------------------
ERROR: ✗ getting latest version: URL "https://REDACTED:REDACTED@repo.example.org/releases/org/example/company/wrong-artifact/maven-metadata.xml" not found or in error
```

### Impact

User credentials/token used to authenticate against a private maven repository can be leaked in clear-text in console or CI logs.

## References
- https://github.com/updatecli/updatecli/security/advisories/GHSA-v34r-vj4r-38j6
- https://nvd.nist.gov/vuln/detail/CVE-2025-24355
- https://github.com/updatecli/updatecli/commit/344b28091ffeca5ed32e8d0f9eda542842fcd3fa
- https://github.com/updatecli/updatecli
- https://www.updatecli.io/docs/plugins/resource/maven
