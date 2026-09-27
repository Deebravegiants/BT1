# [M] Creation of Temporary File in Directory with Insecure Permissions in auto-generated Java, Scala code

## Summary
Severity: Medium
Advisory: GHSA-cqxr-xf2w-943w
CVE: CVE-2021-21430
CWE: CWE-269, CWE-377, CWE-378, CWE-379, CWE-668
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2021-05-11
Source: https://github.com/advisories/GHSA-cqxr-xf2w-943w
Type: github-advisory

## Affected
- Maven: `org.openapitools:openapi-generator` — affected >=0 <5.1.0

## Details
### Impact

**This vulnerability impacts generated code.** If this code was generated as a one-off occasion, not as a part of an automated CI/CD process, this code will remain vulnerable until fixed manually!

On Unix-Like systems, the system temporary directory is shared between all local users. When files/directories are created, the default `umask` settings for the process are respected. As a result, by default, most processes/apis will create files/directories with the permissions `-rw-r--r--` and `drwxr-xr-x` respectively, unless an API that explicitly sets safe file permissions is used.

This vulnerability exists due to the use of the JDK method `File.createTempFile`. This method creates an insecure temporary files that can leave application and system data vulnerable to exposure.

Auto-generated code (Java, Scala) that deals with uploading or downloading binary data through API endpoints will create insecure temporary files during the process. For example, if the API endpoint returns a PDF file, the auto-generated clients will first download the PDF into a insecure temporary file that can be read by anyone on the system.

Affected generators: 
 - Java
   - `okhttp-gson` (default library)
     https://github.com/OpenAPITools/openapi-generator/blob/d85f61ff0cfd6b8cd7063a63f302998a51466269/modules/openapi-generator/src/main/resources/Java/libraries/okhttp-gson/ApiClient.mustache#L1085-L1088
   - `jersey2`
     https://github.com/OpenAPITools/openapi-generator/blob/d85f61ff0cfd6b8cd7063a63f302998a51466269/modules/openapi-generator/src/main/resources/Java/libraries/jersey2/ApiClient.mustache#L1035-L1038
   - `resteasy`
     https://github.com/OpenAPITools/openapi-generator/blob/d85f61ff0cfd6b8cd7063a63f302998a51466269/modules/openapi-generator/src/main/resources/Java/libraries/resteasy/ApiClient.mustache#L604-L607
   - `retrofit2`
      https://github.com/OpenAPITools/openapi-generator/blob/d85f61ff0cfd6b8cd7063a63f302998a51466269/modules/openapi-generator/src/main/resources/Java/libraries/retrofit2/play26/ApiClient.mustache#L202-L208
 - Scala
   - `scala-finch`
      https://github.com/OpenAPITools/openapi-generator/blob/764a3b044c19fadf4a0789473cde96a65b77868a/modules/openapi-generator/src/main/resources/scala-finch/api.mustache#L83-L88
   - `scala-akka`
      https://github.com/OpenAPITools/openapi-generator/blob/150e24dc553a8ea5230ffb938ed3e6020e972faa/modules/openapi-generator/src/main/resources/scala-akka-http-server/multipartDirectives.mustache#L71-L73

### Patches

The issue has been patched by changing the generated code to use the JDK method `Files.createTempFile` and released in the v5.1.0 stable version.

This vulnerability has the same root cause as CVE-2021-21364 from the `swagger-api/swagger-codegen` project as this project and that one both share the same original source tree.
https://github.com/swagger-api/swagger-codegen/security/advisories/GHSA-hpv8-9rq5-hq7w

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [OpenAPI Generator Github repo](https://github.com/openAPITools/openapi-generator/)
* Email us at [security@openapitools.org](mailto:security@openapitools.org)

## References
- https://github.com/OpenAPITools/openapi-generator/security/advisories/GHSA-cqxr-xf2w-943w
- https://nvd.nist.gov/vuln/detail/CVE-2021-21430
- https://github.com/OpenAPITools/openapi-generator/pull/8787
- https://github.com/OpenAPITools/openapi-generator/pull/8791
- https://github.com/OpenAPITools/openapi-generator/pull/9348
- https://github.com/OpenAPITools/openapi-generator
