# [?] Patched Fix Inefficient Regular Expression Complexity Regular Expression Denial of Service (#4271)

## Summary
Severity: Unknown
Chain: Iron Fish
Component: iron-fish/ironfish
Published: 2023-09-14
Source: https://github.com/iron-fish/ironfish/commit/fe04b02fe6fd5abc916e3715f11a41e6ee4e11bc
Type: security-commit

## Details
Patched Fix Inefficient Regular Expression Complexity Regular Expression Denial of Service (#4271)

Affected of this project are vulnerable to Regular Expression Denial of Service (ReDoS) due to the usage of an insecure regular expression within the result variable.

```js
const wrap = require("word-wrap"); for (let i = 0; i <= 10; i++) { const attack = "a" + "t".repeat(i * 10_00000); const start = performance.now(); wrap( attack, { trim: true }, ); console.log(`${attack.length} characters: ${performance.now() - start}ms`); }
```
Denial of Service (DoS) describes a family of attacks, all aimed at making a system inaccessible to its original and legitimate users. There are many types of DoS attacks, ranging from trying to clog the network pipes to the system by generating a large volume of traffic from many machines (a Distributed Denial of Service - DDoS - attack) to sending crafted requests that cause a system to crash or take a disproportional amount of time to process.

CWE-1333
`CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L`

Co-authored-by: jowparks <joe@iflabs.network>
Co-authored-by: Rohan Jadvani <5459049+rohanjadvani@users.noreply.github.com>
