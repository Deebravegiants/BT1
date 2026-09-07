# [M] Cross-site Scripting in ZenUML

## Summary
Severity: Medium
Advisory: GHSA-q6xv-jm4v-349h
CVE: CVE-2024-38527
CWE: CWE-79, CWE-80
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-06-26
Source: https://github.com/advisories/GHSA-q6xv-jm4v-349h
Type: github-advisory

## Affected
- npm: `@zenuml/core` — affected >=0 <3.23.25

## Details
### Summary

Markdown-based comments in the ZenUML diagram syntax are susceptible to Cross-site Scripting (XSS).

### Details

The comment feature allows the user to attach small notes for reference. This feature allows the user to enter in their comment in markdown comment, allowing them to use common markdown features, such as `**` for bolded text. However, the markdown text is currently not sanitized before rendering, allowing an attacker to enter a malicious payload for the comment which leads to XSS.

https://github.com/mermaid-js/zenuml-core/blob/dcfee8cde42673c09e19401f43ad8506658c8442/src/components/DiagramFrame/SeqDiagram/MessageLayer/Block/Statement/Comment/Comment.vue#L65

### PoC

```
// p<img onerror=alert(1) src=""/>
A->B:hi
```

Above is a POC diagram payload that results in an XSS.

Here is a similar POC in mermaid.live: https://mermaid.live/edit#pako:eNpNjrFuwyAQhl8F3dRK1DaQGhs1kVq1Y6duFQsylwTVgEWw1MTyuxc5S7df39399y0wRIug4IZh9qMOdU2mF-dPJAZMKaa9GTHlB_ZILmnYa9BQH3R4fTq8qbMDCh6TN86WhkUHQjTkM3rUoEq0Jv2Ui7CWPTPn-HUNA6icZqQwT9ZkfHfmlIwHdTTjpVC0Lsf0eVfazChMJoBa4BdUL6uGC8n7TrCGd5zCFRRnXbVjvBVNK3gJXbtSuMVYSlnFC-Kyf961UshWbmXf2-y_xcf29c7WP2yrVC0

### Impact

This puts existing applications that use ZenUML **unsandboxed** at risk of arbitrary JavaScript execution when rendering user-controlled diagrams.

## References
- https://github.com/mermaid-js/zenuml-core/security/advisories/GHSA-q6xv-jm4v-349h
- https://nvd.nist.gov/vuln/detail/CVE-2024-38527
- https://github.com/mermaid-js/zenuml-core/commit/ad7545b33f5f27466cbf357beb65969ca1953e3c
- https://github.com/mermaid-js/zenuml-core
