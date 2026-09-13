# [H] GitProxy New Branch Approval Exploit

## Summary
Severity: High
Advisory: GHSA-39p2-8hq9-fwj6
CVE: CVE-2025-54585
CWE: CWE-285
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:P/VC:N/VI:H/VA:N/SC:N/SI:H/SA:N (CVSS_V4)
Published: 2025-07-30
Source: https://github.com/advisories/GHSA-39p2-8hq9-fwj6
Type: github-advisory

## Affected
- npm: `@finos/git-proxy` — affected >=0 <1.19.2

## Details
### Summary
An attacker can exploit the way GitProxy handles new branch creation to bypass the approval of prior commits on the parent branch.

Because it can greatly affect system integrity, we classify this as a High impact vulnerability.

### Details
GitProxy checks for the `0000000000000000000000000000000000000000` hash to detect new branches. This is used to process the commit accordingly in both `getDiff.ts` and `parsePush.ts`. However, the logic can be exploited as follows:

1. Make a commit in branch `a` (could be `main`)
2. Make a new branch `b` from that commit
3. Make a new commit in `b`, then approve it/get it approved
4. Go back to `a`, and attempt to push this commit to the proxy

The unapproved commit from `a` will be pushed to the remote.

### PoC
To reproduce this vulnerability:

1. Clone the target repository and make an unapproved commit on a mainline branch (e.g. main):

```bash
git checkout -b a origin/main
echo "DEBUG=true" > config.env
git add config.env
git commit -m "Sensitive debug config"
git push proxy a
```

2. Without approving/getting the commit approved on branch `a`, create a new branch `b` based on it:

```bash
git checkout -b b
echo "feature x implemented" > feature.txt
git add feature.txt
git commit -m "Feature implementation"
git push proxy b
```

3. Approve/get approval for the push to branch `b`.

4. Now attempt to push the original unapproved commit from branch `a`:

```bash
git checkout a
git push proxy a
```

Prior to `1.19.2`, this results in unapproved commits from `a` getting pushed without any policy checks or explicit approval.

From `1.19.2` onwards, this flow will allow pushing all commits to branch `b` (and explicit approval will be asked for the changes on `b` only). However, commits on branch `a` now require approval on push. If merging branch `b` into `a`, this also requires explicit approval of the (previously unapproved) commits originating from `a` to prevent loopholes.

### Impact
The vulnerability impacts all users or organizations relying on GitProxy to enforce policy and prevent unapproved changes. It requires no elevated privileges beyond regular push access, and no extra user interaction. It does however, require a GitProxy administrator or designated user (`canUserApproveRejectPush`) to approve pushes to the child branch.

## References
- https://github.com/finos/git-proxy/security/advisories/GHSA-39p2-8hq9-fwj6
- https://nvd.nist.gov/vuln/detail/CVE-2025-54585
- https://github.com/finos/git-proxy/commit/a620a2f33c39c78e01783a274580bf822af3cc3a
- https://github.com/finos/git-proxy/commit/f99fe42082eab0970e4cd0acdc3421a527a7e531
- https://github.com/finos/git-proxy
- https://github.com/finos/git-proxy/releases/tag/v1.19.2
