# [H] Temporary Directory Hijacking to Local Privilege Escalation Vulnerability in org.springframework.boot:spring-boot

## Summary
Severity: High
Advisory: GHSA-cm59-pr5q-cw85
CVE: CVE-2022-27772
CWE: CWE-377, CWE-379, CWE-668
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2022-07-11
Source: https://github.com/advisories/GHSA-cm59-pr5q-cw85
Type: github-advisory

## Affected
- Maven: `org.springframework.boot:spring-boot` — affected >=0 <2.2.11.RELEASE

## Details
spring-boot versions prior to version `v2.2.11.RELEASE` was vulnerable to temporary directory hijacking. This vulnerability impacted the `org.springframework.boot.web.server.AbstractConfigurableWebServerFactory.createTempDir` method.

The vulnerable method is used to create a work directory for embedded web servers such as Tomcat and Jetty. The directory contains configuration files, JSP/class files, etc. If a local attacker got the permission to write in this directory, they could completely take over the application (ie. local privilege escalation).

#### Impact Location

This vulnerability impacted the following source location:

```java
	/**
	 * Return the absolute temp dir for given web server.
	 * @param prefix server name
	 * @return the temp dir for given server.
	 */
	protected final File createTempDir(String prefix) {
		try {
			File tempDir = File.createTempFile(prefix + ".", "." + getPort());
			tempDir.delete();
			tempDir.mkdir();
			tempDir.deleteOnExit();
			return tempDir;
		}
```
\- https://github.com/spring-projects/spring-boot/blob/ce70e7d768977242a8ea6f93188388f273be5851/spring-boot-project/spring-boot/src/main/java/org/springframework/boot/web/server/AbstractConfigurableWebServerFactory.java#L165-L177

This vulnerability exists because `File.mkdir` returns `false` when it fails to create a directory, it does not throw an exception. As such, the following race condition exists:

```java
File tmpDir =File.createTempFile(prefix + ".", "." + getPort()); // Attacker knows the full path of the file that will be generated
// delete the file that was created
tmpDir.delete(); // Attacker sees file is deleted and begins a race to create their own directory before Jetty.
// and make a directory of the same name
// SECURITY VULNERABILITY: Race Condition! - Attacker beats java code and now owns this directory
tmpDir.mkdirs(); // This method returns 'false' because it was unable to create the directory. No exception is thrown.
// Attacker can write any new files to this directory that they wish.
// Attacker can read any files created by this process.
```

### Prerequisites

This vulnerability impacts Unix-like systems, and very old versions of Mac OSX and Windows as they all share the system temporary directory between all users.

### Patches

This vulnerability was inadvertently fixed as a part of this patch: https://github.com/spring-projects/spring-boot/commit/667ccdae84822072f9ea1a27ed5c77964c71002d

This vulnerability is patched in versions `v2.2.11.RELEASE` or later.

### Workarounds

Setting the `java.io.tmpdir` system environment variable to a directory that is exclusively owned by the executing user will fix this vulnerability for all operating systems.

## References
- https://github.com/JLLeitschuh/security-research/security/advisories/GHSA-cm59-pr5q-cw85
- https://nvd.nist.gov/vuln/detail/CVE-2022-27772
- https://github.com/spring-projects/spring-boot/commit/667ccdae84822072f9ea1a27ed5c77964c71002d
- https://github.com/spring-projects/spring-boot
