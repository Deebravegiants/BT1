# [C] Remote Code Execution in AjaxNetProfessional

## Summary
Severity: Critical
Advisory: GHSA-6r7c-6w96-8pvw
CVE: CVE-2021-23758
CWE: CWE-502
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-12-07
Source: https://github.com/advisories/GHSA-6r7c-6w96-8pvw
Type: github-advisory

## Affected
- NuGet: `AjaxNetProfessional` — affected >=0 <21.11.29.1

## Details
### Overview

Affected versions of this package are vulnerable to Deserialization of Untrusted Data due to the possibility of deserialization of arbitrary .NET classes, which can be abused to gain remote code execution.

### Description

Serialization is a process of converting an object into a sequence of bytes which can be persisted to a disk or database or can be sent through streams. The reverse process of creating object from sequence of bytes is called deserialization. Serialization is commonly used for communication (sharing objects between multiple hosts) and persistence (store the object state in a file or a database). It is an integral part of popular protocols like Remote Method Invocation (RMI), Java Management Extension (JMX), Java Messaging System (JMS), Action Message Format (AMF), Java Server Faces (JSF) ViewState, etc.

Deserialization of untrusted data (CWE-502), is when the application deserializes untrusted data without sufficiently verifying that the resulting data will be valid, letting the attacker to control the state or the flow of the execution.

Java deserialization issues have been known for years. However, interest in the issue intensified greatly in 2015, when classes that could be abused to achieve remote code execution were found in a popular library (Apache Commons Collection). These classes were used in zero-days affecting IBM WebSphere, Oracle WebLogic and many other products.

An attacker just needs to identify a piece of software that has both a vulnerable class on its path, and performs deserialization on untrusted data. Then all they need to do is send the payload into the deserializer, getting the command executed.

Developers put too much trust in Java Object Serialization. Some even de-serialize objects pre-authentication. When deserializing an Object in Java you typically cast it to an expected type, and therefore Java's strict type system will ensure you only get valid object trees. Unfortunately, by the time the type checking happens, platform code has already created and executed significant logic. So, before the final type is checked a lot of code is executed from the readObject() methods of various objects, all of which is out of the developer's control. By combining the readObject() methods of various classes which are available on the classpath of the vulnerable application an attacker can execute functions (including calling Runtime.exec() to execute local OS commands).

### Releases

Releases before version 21.11.29.1 are affected. Please be careful to download any binary DLL from other web sites, especially we found NuGet packages not owned by us that contain vulnerable versions.

### Workarounds

There is no workaround available that addresses all issues except updating to latest version from GitHub.

### References

Find original CVE posting here: https://security.snyk.io/vuln/SNYK-DOTNET-AJAXPRO2-1925971

Note: the official Ajax.NET Professional (AjaxPro) NuGet package is available here: https://www.nuget.org/packages/AjaxNetProfessional/

### For more information

If you have any questions or comments about this advisory:
* Open an issue on this GitHub repository

## References
- https://github.com/michaelschwarz/Ajax.NET-Professional/security/advisories/GHSA-6r7c-6w96-8pvw
- https://nvd.nist.gov/vuln/detail/CVE-2021-23758
- https://github.com/michaelschwarz/Ajax.NET-Professional/commit/b0e63be5f0bb20dfce507cb8a1a9568f6e73de57
- https://github.com/michaelschwarz/Ajax.NET-Professional
- https://security.snyk.io/vuln/SNYK-DOTNET-AJAXPRO2-1925971
- http://packetstormsecurity.com/files/175677/AjaxPro-Deserialization-Remote-Code-Execution.html
