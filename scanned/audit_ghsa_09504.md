# [H] OpenMRS ModuleResourcesServlet has Path Traversal that Leads to Arbitrary File Read

## Summary
Severity: High
Advisory: GHSA-jjgj-cx3q-pw4w
CVE: CVE-2026-40075
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-05-04
Source: https://github.com/advisories/GHSA-jjgj-cx3q-pw4w
Type: github-advisory

## Affected
- Maven: `org.openmrs.web:openmrs-web` — affected >=0
- Maven: `org.openmrs.web:openmrs-web` — affected >=2.8.0 <2.8.6

## Details
## Affected Versions

version ≤ 2.7.8 (latest version at time of disclosure)

https://github.com/openmrs/openmrs-core

## Impact

The `/openmrs/moduleResources/{moduleid}` endpoint in OpenMRS Core is vulnerable to a path traversal attack. The `ModuleResourcesServlet` does not properly validate user-supplied path input, allowing an attacker to traverse directories and read arbitrary files from the server filesystem (e.g., `/etc/passwd`, application configuration files containing database credentials).

This endpoint serves static module resources (CSS, JS, images) and is **not protected by authentication filters**, as these resources are required for rendering the login page. Therefore, this vulnerability can be exploited by an **unauthenticated** attacker.

> **Note:** Successful exploitation requires the target deployment to run on **Apache Tomcat < 8.5.31**, where the `..;` path parameter bypass is not mitigated by the container. Deployments on Tomcat ≥ 8.5.31 / ≥ 9.0.10 are protected at the container level, though the underlying code defect remains.
> 

## Steps to Reproduce

1. Identify a valid installed module ID on the target OpenMRS instance (e.g., `legacyui`).
2. Send the following HTTP request:

<img width="1038" height="798" alt="image" src="https://github.com/user-attachments/assets/7d10ee0e-4d81-4c01-bc84-a1bf5715f170" />

3. The server responds with HTTP 200 and the contents of `/etc/passwd`:

<img width="1028" height="843" alt="image" src="https://github.com/user-attachments/assets/b6806a7e-ff52-4f51-8f7f-7ea4e9754d10" />


## Root Cause Analysis

The vulnerability exists in `ModuleResourcesServlet.java` (`web/src/main/java/org/openmrs/module/web/ModuleResourcesServlet.java`).

The `getFile()` method constructs a filesystem path from user-controlled input without performing path boundary validation:

```java
protected File getFile(HttpServletRequest request) {
    // Step 1: User-controlled path input
    String path = request.getPathInfo();

    // Step 2: Extract module from path prefix
    Module module = ModuleUtil.getModuleForPath(path);
    if (module == null) { return null; }

    // Step 3: Strip module ID prefix — no traversal check
    String relativePath = ModuleUtil.getPathForResource(module, path);

    // Step 4: Concatenate into absolute path
    String realPath = getServletContext().getRealPath("")
        + MODULE_PATH
        + module.getModuleIdAsPath()
        + "/resources"
        + relativePath;  // contains "/../../../etc/passwd"

    realPath = realPath.replace("/", File.separator);

    // Step 5: No normalize().startsWith() boundary check
    File f = new File(realPath);
    if (!f.exists()) { return null; }

    return f;  // Arbitrary file returned to client
}
```

The helper method `ModuleUtil.getPathForResource()` only strips the module ID prefix and performs no sanitization:

```java
public static String getPathForResource(Module module, String path) {
    if (path.startsWith("/")) {
        path = path.substring(1);
    }
    return path.substring(module.getModuleIdAsPath().length());
    // Returns unsanitized remainder, e.g., "/../../../../../../etc/passwd"
}
```

The resulting path resolves as:

```
{webapp}/WEB-INF/view/module/legacyui/resources/../../../../../../etc/passwd
  → /etc/passwd
```

Notably, the same codebase already implements correct path traversal protection in `StartupFilter.java`:

```java
// StartupFilter.java — correct protection
fullFilePath = fullFilePath.resolve(httpRequest.getPathInfo());
if (!(fullFilePath.normalize().startsWith(filePath))) {
    log.warn("Detected attempted directory traversal...");
    return;  // Request rejected
}
```

This check is absent from `ModuleResourcesServlet`.

## Remediation

Add a path boundary check after constructing `realPath` and before returning the `File` object. The fix should use `normalize()` + `startsWith()` to ensure the resolved path stays within the allowed module resources directory:

```java
File f = new File(realPath);
Path allowedBase = Paths.get(getServletContext().getRealPath(""), "WEB-INF", "view", "module");
if (!f.toPath().normalize().startsWith(allowedBase.normalize())) {
    log.warn("Blocked path traversal attempt: {}", request.getPathInfo());
    return null;
}
```

This is consistent with the existing pattern used in `StartupFilter.java` and `TestInstallUtil.java` within the same project.

## References
- https://github.com/openmrs/openmrs-core/security/advisories/GHSA-jjgj-cx3q-pw4w
- https://nvd.nist.gov/vuln/detail/CVE-2026-40075
- https://github.com/openmrs/openmrs-core
