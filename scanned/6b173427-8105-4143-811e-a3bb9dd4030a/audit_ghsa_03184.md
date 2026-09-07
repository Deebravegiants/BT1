# [C] Creation of Temporary File in Directory with Insecure Permissions in the OpenAPI-Generator online generator

## Summary
Severity: Critical
Advisory: GHSA-23x4-m842-fmwf
CVE: CVE-2021-21428
CWE: CWE-269, CWE-377, CWE-378, CWE-379, CWE-668
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2021-05-11
Source: https://github.com/advisories/GHSA-23x4-m842-fmwf
Type: github-advisory

## Affected
- Maven: `org.openapitools:openapi-generator-online` — affected >=0 <5.1.0

## Details
### Impact

On Unix like systems, the system's temporary directory is shared between all users on that system. A collocated user can observe the process of creating a temporary sub directory in the shared temporary directory and race to complete the creation of the temporary subdirectory.

This vulnerability is local privilege escalation because the contents of the outputFolder can be appended to by an attacker. As such, code written to this directory, when executed can be attacker controlled.

openapi-generator-online creates insecure temporary folders with `File.createTempFile` during the code generation process. The insecure temporary folders store the auto-generated files which can be read and appended to by any users on the system.

### Vulnerable Code

https://github.com/OpenAPITools/openapi-generator/blob/c6530519975341d7784a252132b2f0854f488901/modules/openapi-generator-online/src/main/java/org/openapitools/codegen/online/service/Generator.java#L184-L187

This vulnerability exists due to a race condition between the deletion of the randomly generated temporary file and the creation of the temporary directory.

```java
File outputFolder = File.createTempFile("codegen-", "-tmp"); // Attacker knows the full path of the file that will be generated
// delete the file that was created
outputFolder.delete(); // Attacker sees file is deleted and begins a race to create their own directory before the code generator
// and make a directory of the same name
// SECURITY VULNERABILITY: Race Condition! - Attacker beats the code generator and now owns this directory
outputFolder.mkdir();
```

### Patches
The issue has been patched by changing the underlying logic to use `Files.createTempFile` and has been released in the v5.1.0 stable version.

This vulnerability has the same root cause as CVE-2021-21363 from the `swagger-api/swagger-codegen` project as this project and that one both share the same original source tree.
See: https://github.com/swagger-api/swagger-codegen/security/advisories/GHSA-pc22-3g76-gm6j

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [OpenAPI Generator Github repo](https://github.com/openAPITools/openapi-generator/)
* Email us at [security@openapitools.org](mailto:security@openapitools.org)

## References
- https://github.com/OpenAPITools/openapi-generator/security/advisories/GHSA-23x4-m842-fmwf
- https://github.com/swagger-api/swagger-codegen/security/advisories/GHSA-pc22-3g76-gm6j
- https://nvd.nist.gov/vuln/detail/CVE-2021-21428
- https://github.com/OpenAPITools/openapi-generator/pull/8788
- https://github.com/OpenAPITools/openapi-generator
- https://github.com/OpenAPITools/openapi-generator/blob/c6530519975341d7784a252132b2f0854f488901/modules/openapi-generator-online/src/main/java/org/openapitools/codegen/online/service/Generator.java#L184-L187
