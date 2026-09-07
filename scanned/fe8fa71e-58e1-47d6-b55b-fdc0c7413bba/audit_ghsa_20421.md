# [H] Inefficient Regular Expression Complexity in marked

## Summary
Severity: High
Advisory: GHSA-rrrm-qjm4-v8hf
CVE: CVE-2022-21680
CWE: CWE-1333, CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-01-14
Source: https://github.com/advisories/GHSA-rrrm-qjm4-v8hf
Type: github-advisory

## Affected
- npm: `marked` — affected >=0 <4.0.10

## Details
### Impact

_What kind of vulnerability is it?_

Denial of service.

The regular expression `block.def` may cause catastrophic backtracking against some strings.
PoC is the following.

```javascript
import * as marked from "marked";

marked.parse(`[x]:${' '.repeat(1500)}x ${' '.repeat(1500)} x`);
```

_Who is impacted?_

Anyone who runs untrusted markdown through marked and does not use a worker with a time limit.

### Patches

_Has the problem been patched?_

Yes

_What versions should users upgrade to?_

4.0.10

### Workarounds

_Is there a way for users to fix or remediate the vulnerability without upgrading?_

Do not run untrusted markdown through marked or run marked on a [worker](https://marked.js.org/using_advanced#workers) thread and set a reasonable time limit to prevent draining resources.

### References

_Are there any links users can visit to find out more?_

- https://marked.js.org/using_advanced#workers
- https://owasp.org/www-community/attacks/Regular_expression_Denial_of_Service_-_ReDoS

### For more information

If you have any questions or comments about this advisory:

* Open an issue in [marked](https://github.com/markedjs/marked)

## References
- https://github.com/markedjs/marked/security/advisories/GHSA-rrrm-qjm4-v8hf
- https://nvd.nist.gov/vuln/detail/CVE-2022-21680
- https://github.com/markedjs/marked/commit/c4a3ccd344b6929afa8a1d50ac54a721e57012c0
- https://github.com/markedjs/marked
- https://github.com/markedjs/marked/releases/tag/v4.0.10
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/AIXDMC3CSHYW3YWVSQOXAWLUYQHAO5UX
