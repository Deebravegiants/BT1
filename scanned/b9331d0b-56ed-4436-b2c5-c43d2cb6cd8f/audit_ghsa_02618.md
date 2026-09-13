# [C] Improper Neutralization of Special Elements used in an OS Command ('OS Command Injection') in ZMarkdown

## Summary
Severity: Critical
Advisory: GHSA-2c83-wfv3-q25f
CWE: CWE-78
Ecosystem: npm
Published: 2021-09-07
Source: https://github.com/advisories/GHSA-2c83-wfv3-q25f
Type: github-advisory

## Affected
- npm: `rebber` — affected >=0 <5.2.1

## Details
### Impact

A Remote Command Execution vulnerability was found in the rebber module,
which allowed execution of arbitrary commands. The reported problem came
from CodeBlocks, which could be escaped to insert malicious LaTeX.

Anyone using `rebber` without sanitation of code content or a custom
macro is impacted by this vulnerability. Here is an example of a Markdown
content that will exploit the vulnerability:

````markdown
```
\end{CodeBlock}

\immediate\write18{COMMAND > outputrce}
\input{outputrce}

\begin{CodeBlock}{text}
```
````

Will insert into the generated LaTeX the result of executing
`COMMAND` on the system.

### Patches

The vulnerability has been patched in version 5.2.1.
If impacted, you should update to this version as soon as possible.

### Workarounds

It is possible to mitigate the vulnerability without upgrading by using a
custom code macro. Please make sure this custom macro escapes your
closing LaTeX sequence. For the example above, use:

```javascript
const escaped = content.replace(new RegExp('\\\\end\\s*{CodeBlock}', 'g'), '')
```

### For more information

If you have any questions or comments about this advisory, open an issue in [ZMarkdown](https://github.com/zestedesavoir/zmarkdown/issues).

## References
- https://github.com/zestedesavoir/zmarkdown/security/advisories/GHSA-2c83-wfv3-q25f
- https://github.com/zestedesavoir/zmarkdown
