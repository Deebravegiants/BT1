# [H] Pebble has Arbitrary Local File Inclusion (LFI) Vulnerability via `include` macro

## Summary
Severity: High
Advisory: GHSA-p75g-cxfj-7wrx
CVE: CVE-2025-1686
CWE: CWE-73
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2025-02-28
Source: https://github.com/advisories/GHSA-p75g-cxfj-7wrx
Type: github-advisory

## Affected
- Maven: `io.pebbletemplates:pebble` — affected >=0

## Details
### Summary

If untrusted user input is used to dynamically create a `PebbleTemplate` with the method `PebbleEngine#getLiteralTemplate`, then an attacker can include arbitrary local files from the file system into the generated template, leaking potentially sensitive information into the output of `PebbleTemplate#evaluate`. This is done via the `include` macro.

### Details

The `include` macro calls `PebbleTempateImpl#resolveRelativePath` with the `relativePath` argument passed within the template:

Example template:
```
{% include [relativePath] %}
```
When `resolveRelativePath` is called, the `relativePath`  is resolved against the `PebbleTemplateImpl.name` variable.

```java
  /**
   * This method resolves the given relative path based on this template file path.
   *
   * @param relativePath the path which should be resolved.
   * @return the resolved path.
   */
  public String resolveRelativePath(String relativePath) {
    String resolved = this.engine.getLoader().resolveRelativePath(relativePath, this.name);
    if (resolved == null) {
      return relativePath;
    } else {
      return resolved;
    }
  }
```
https://github.com/PebbleTemplates/pebble/blob/82ad7fcf9e9eaa45ee82ae3335a1409d19c10263/pebble/src/main/java/io/pebbletemplates/pebble/template/PebbleTemplateImpl.java#L380

Unfortunately, when the template is created from a string, as is the case when `PebbleEngine#getLiteralTemplate` is used, the `PebbleTemplateImpl.name` variable is actually the entirety of the contents of the template, not a filename as the logic expects. The net result is that the `relativePath` is resolved against the system root directory. As a result, files accessible from the root directory of the filesystem can be included into a template. 

### PoC

The following test demonstrates the vulnerability:

```java
PebbleEngine e = new PebbleEngine.Builder().build();

String templateString = """
        {% include '/etc/passwd' %}
        """;
PebbleTemplate template = e.getLiteralTemplate(templateString);

try (final Writer writer = new StringWriter()) {
    template.evaluate(writer, new HashMap<>());
    System.out.println(writer);
}
```

As an attacker, the following malicious template demonstrates the vulnerability:

```
{% include '/etc/passwd' %}
```

### Impact

This is an arbitrary  Local File Inclusion (LFI) vulnerability. It can allow attackers to exfiltrate the contents of the local filesystem, including sensitive files into `PebbleTemplate` output. This can also be used to access the `/proc` filesystem which can give an attacker access to environment variables.

### Fix

There exists no published fix for this vulnerability. The best way to mitigate this vulnerability is to disable the `include` macro in Pebble Templates.

The following can safeguard your application from this vulnerability:

```java
new PebbleEngine.Builder()
            .registerExtensionCustomizer(new DisallowExtensionCustomizerBuilder()
                    .disallowedTokenParserTags(List.of("include"))
                    .build())
            .build();
```

### Report Timeline

Vulnerability was reported under the Open Source Security Foundation (OpenSSF) [Model Outbound Vulnerability Disclosure Policy: Version 0.1](https://openssf.org/about/vulnerability-disclosure-policy/).

 - [Jul 15, 2024](https://github.com/PebbleTemplates/pebble/issues/680#issue-2409727829) Maintainer Contacted to enable private vulnerability reporting
 - [Jul 18, 2024](https://github.com/PebbleTemplates/pebble/issues/680#issuecomment-2236970984) I opened a GHSA 
 to report this vulnerability to the maintainer https://github.com/PebbleTemplates/pebble/security/advisories/GHSA-7c6h-hmf9-7wj7 (private link)
 - Jul 29, 2024 GHSA updated to ping maintainer about vulnerability, no response
 - Oct 1, 2024 GHSA updated to ping maintainer about vulnerability, no response
 - Nov 15, 2024 GHSA updated to inform maintainer that disclosure timeline had lapsed, no response.
 - Feb 19, 2025 GHSA updated to inform maintainer that disclosure would occur imminently, no response.
 - Feb 24, 2025 this GHSA was created to disclose this vulnerability **without a patch available**.

For further discussion, see this issue: https://github.com/PebbleTemplates/pebble/issues/688

### Credit

This vulnerability was discovered by @JLLeitschuh while at [Chainguard Labs](https://www.chainguard.dev). Jonathan is currently independent.

## References
- https://github.com/JLLeitschuh/security-research/security/advisories/GHSA-p75g-cxfj-7wrx
- https://nvd.nist.gov/vuln/detail/CVE-2025-1686
- https://github.com/PebbleTemplates/pebble/issues/680
- https://github.com/PebbleTemplates/pebble/issues/688
- https://github.com/PebbleTemplates/pebble/pull/715
- https://github.com/PebbleTemplates/pebble/commit/b3451c8f305a1a248fbcc2363fd307d0baaee329
- https://github.com/PebbleTemplates/pebble
- https://pebbletemplates.io/wiki/tag/include
- https://security.snyk.io/vuln/SNYK-JAVA-IOPEBBLETEMPLATES-8745594
