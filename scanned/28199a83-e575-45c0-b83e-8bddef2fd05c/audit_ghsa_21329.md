# [M] Jadx-gui vulnerable to swing HTML Denial of Service (DoS) attack

## Summary
Severity: Medium
Advisory: GHSA-3r7j-8mqh-6qhx
CVE: CVE-2022-39259
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-10-20
Source: https://github.com/advisories/GHSA-3r7j-8mqh-6qhx
Type: github-advisory

## Affected
- Maven: `io.github.skylot:jadx-plugins-api` — affected >=0 <1.4.5

## Details
### Impact
Using jadx-gui to open a special zip file with entry containing HTML sequence like `<html><frame>` will cause interface to get stuck and throw exceptions like:
```
java.lang.RuntimeException: Can't build aframeset, BranchElement(frameset) 1,3
:no ROWS or COLS defined.
	at java.desktop/javax.swing.text.html.HTMLEditorKit$HTMLFactory.create(HTMLEditorKit.java:1387)
	at java.desktop/javax.swing.plaf.basic.BasicHTML$BasicHTMLViewFactory.create(BasicHTML.java:379)
	at java.desktop/javax.swing.text.CompositeView.loadChildren(CompositeView.java:112)
```

### References
https://www.oracle.com/java/technologies/javase/seccodeguide.html

Guideline 3-7 / INJECT-7: Disable HTML display in Swing components:

Many Swing pluggable look-and-feels interpret text in certain components starting with <html> as HTML. If the text is from an untrusted source, an adversary may craft the HTML such that other components appear to be present or to perform inclusion attacks.

To disable the HTML render feature, set the "html.disable" client property of each component to Boolean.TRUE (no other Boolean true instance will do).
```java
label.putClientProperty("html.disable", true);
```

## References
- https://github.com/skylot/jadx/security/advisories/GHSA-3r7j-8mqh-6qhx
- https://nvd.nist.gov/vuln/detail/CVE-2022-39259
- https://github.com/skylot/jadx
- https://github.com/skylot/jadx/releases/tag/v1.4.5
- https://www.oracle.com/java/technologies/javase/seccodeguide.html
