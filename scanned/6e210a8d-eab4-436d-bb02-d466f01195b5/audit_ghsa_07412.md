# [C] Gitea Actions Artifacts V4 signed URL HMAC ambiguity allows cross-repository artifact read and cross-task upload-state write

## Summary
Severity: Critical
Advisory: GHSA-hg5r-vq93-9fv6
CVE: CVE-2026-58426
CWE: CWE-347
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2026-07-21
Source: https://github.com/advisories/GHSA-hg5r-vq93-9fv6
Type: github-advisory

## Affected
- Go: `code.gitea.io/gitea` — affected >=1.22.0 <1.26.2

## Details
### Summary

Gitea Actions Artifacts V4 signed upload/download URLs can be rewritten to access a different running task and repository context while preserving the original HMAC signature. An attacker with permission to run a Gitea Actions job can turn a signed URL for an attacker-controlled artifact into a URL that reads artifacts from another task context, or writes attacker-controlled data into another task's artifact upload staging context, including in a private repository.

This is one vulnerability with two exploit paths:

- `DownloadArtifact`: cross-task/cross-repository artifact read, giving `C:H`.
- `UploadArtifact`: cross-task artifact staging write and metadata mutation, giving `I:H`.

### Details

The root cause is that the V4 artifact signed URL signature is built from raw concatenated fields without delimiters or length-prefixing:

```go
func (r *artifactV4Routes) buildSignature(endpoint, expires, artifactName string, taskID, artifactID int64) []byte {
        mac := hmac.New(sha256.New, setting.GetGeneralTokenSigningSecret())
        mac.Write([]byte(endpoint))
        mac.Write([]byte(expires))
        mac.Write([]byte(artifactName))
        _, _ = fmt.Fprint(mac, taskID)
        _, _ = fmt.Fprint(mac, artifactID)
        return mac.Sum(nil)
}
```

Affected code: `routers/api/actions/artifactsv4.go:164-171`.

Because `artifactName`, `taskID`, and `artifactID` are concatenated without boundaries, two different URL tuples can produce the same HMAC input. For example:

```text
signed tuple:
artifactName = "artifact-795-153"
taskID       = 48
artifactID   = <attacker artifact id>

forged tuple:
artifactName = "artifact-795-1"
taskID       = 53
artifactID   = 48<attacker artifact id>
```

The final HMAC input suffix is identical:

```text
artifact-795-15348<attacker artifact id>
```

The attacker does not need to know the target artifact's database `artifactID`. The forged URL's `artifactID` only needs to carry digits that preserve the original HMAC input. After verification, the actual target artifact is looked up by target task/run/attempt and `artifactName`, not by the signed `artifactID`.

The signed URL handlers are unauthenticated and use `ArtifactV4Contexter()` only:

```go
m.Group("", func() {
        m.Put("UploadArtifact", r.uploadArtifact)
        m.Get("DownloadArtifact", r.downloadArtifact)
}, ArtifactV4Contexter())
```

Affected code: `routers/api/actions/artifactsv4.go:156-159`.

After verifying the HMAC, `verifySignature()` trusts the URL-controlled `taskID`, loads that task, checks that it is running, and returns the URL-controlled `artifactName`. It parses `artifactID` for the HMAC, but does not load or bind the artifact by that signed artifact ID:

```go
task, err := actions_model.GetTaskByID(ctx, taskID)
...
if task.Status != actions_model.StatusRunning {
        ...
}
...
return task, artifactName, true
```

Affected code: `routers/api/actions/artifactsv4.go:224-267`.

The artifact lookup then uses the URL-selected task's run/attempt plus URL-selected artifact name:

```go
has, err := db.GetEngine(ctx).Where(builder.Eq{
        "run_id": runID,
        "run_attempt_id": runAttemptID,
        "artifact_name": name,
}, builder.Like{"content_encoding", "%/%"}).Get(&art)
```

Affected code: `routers/api/actions/artifactsv4.go:270-278`.

For download, the forged URL reaches `downloadArtifact()`, which verifies the signature, resolves the artifact by the forged task/run/name context, and serves it:

```go
task, artifactName, ok := r.verifySignature(ctx, "DownloadArtifact")
...
artifact, err := r.getArtifactByName(ctx, task.Job.RunID, task.Job.RunAttemptID, artifactName)
...
err = actions.DownloadArtifactV4ReadStorage(ctx.Base, artifact)
```

Affected code: `routers/api/actions/artifactsv4.go:674-693`.

For upload, the forged URL reaches `uploadArtifact()`, which verifies the signature, resolves the target artifact by the forged task/run/name context, appends attacker-controlled data, and updates target artifact metadata:

```go
task, artifactName, ok := r.verifySignature(ctx, "UploadArtifact")
...
artifact, err := r.getArtifactByName(ctx, task.Job.RunID, task.Job.RunAttemptID, artifactName)
...
uploadedLength, err := appendUploadChunkV3(r.fs, ctx, artifact, artifact.RunID, artifact.FileSize)
...
artifact.FileCompressedSize += uploadedLength
artifact.FileSize += uploadedLength
...
actions_model.UpdateArtifactByID(ctx, artifact.ID, artifact)
```

Affected code: `routers/api/actions/artifactsv4.go:382-422`.

The strengthened dynamic PoC also opens the storage object created by the forged upload and verifies that the attacker-controlled bytes were written under the target run and target artifact ID staging path. This demonstrates an unauthorized write primitive into the target artifact upload context. The current PoC does not claim that a finalized artifact download already serves modified bytes; for the integrity path, the confirmed impact is cross-context staging write plus target artifact metadata mutation. In normal artifact upload flow, data in this staging area is what `FinalizeArtifact` later consumes.

V4 artifact creation also appears to omit the existing artifact-name validation:

```go
artifactName := req.Name
...
artifact, err := actions_model.CreateArtifact(ctx, ctx.ActionTask, artifactName, fileName, retentionDays)
```

Affected code: `routers/api/actions/artifactsv4.go:309-337`.

This is a hardening issue, but it is not required for the demonstrated tuple-boundary collision. The crafted artifact names in the PoC use ordinary characters such as letters, digits, and hyphens that would normally be valid. The root cause is the ambiguous signed payload plus the post-verification lookup by URL-selected task/run/name context.

The target task must be running, but that is the normal validity window of these signed URLs. The exploit itself is a deterministic parameter rewrite against the active artifact URL flow, so `AC:L` is appropriate.

Even if the integrity impact is scored conservatively, the `DownloadArtifact` path independently demonstrates cross-repository private artifact disclosure.

Practical constraints:

- the target task must be in `running` state;
- the target task ID and artifact name must be known or predictable;
- for `DownloadArtifact` on newer branches, the target artifact must already be `UploadConfirmed` while the target task is still running. Older V4 implementations differ slightly in artifact lookup/status handling; the PoC validates the branch-specific condition used by each tested release;
- the forged decimal `artifactID` must parse as `int64`;
- the exact storage effect depends on the configured artifact storage backend. The local PoC uses the default non-Azure storage path. The root cause still exists before storage backend handling because the signed URL context is confused before upload/download dispatch.
- the demonstrated exploit applies when Gitea issues its own V4 `UploadArtifact`/`DownloadArtifact` signed URLs. Storage backends or configurations that return direct backend URLs should be assessed separately, because they may bypass these Gitea signed URL handlers.

### PoC

Tested against Gitea `main` checkout:

```text
6a270662690439cabe8582e92c22b04d1f8a3fe9
```

Verified affected versions tested locally:

```text
main       6a27066269  reproduced dynamically
v1.26.1    afdbd9b7c5  reproduced dynamically
v1.25.5    f913d90ab6  reproduced dynamically
v1.24.7    99053ce4fa  reproduced dynamically
v1.23.8    cccd54999a  reproduced dynamically
v1.22.6    8eefa1f6de  reproduced dynamically with Go 1.22.12 test toolchain
v1.21.11   V4 artifactsv4.go route not present in routers/api/actions; not affected by this V4 signed URL path as tested
```

Unless otherwise noted, the affected code snippets and line numbers above refer to the tested `main` checkout `6a27066269`. Older release branches contain the same vulnerable signed URL construction and post-verification context confusion, but line numbers and artifact lookup details differ slightly between releases. For example, newer code includes `run_attempt_id` in the artifact lookup, while older V4 implementations look up by run/name/path/content-encoding. These differences do not affect the demonstrated HMAC boundary-collision primitive.

For `main`, `v1.26.1`, and `v1.25.5`, the PoC uses the private `user2/repo2` fixture and demonstrates cross-repository artifact read. For `v1.24.7`, `v1.23.8`, and `v1.22.6`, the compatible test fixtures differ, so the portable PoC demonstrates the same signed URL rewrite across task/run contexts; `v1.22.6` creates the target artifact inside the test because that release does not include the newer artifact fixture file.

The private-repository disclosure impact is demonstrated on releases with suitable private repository fixtures; on older fixtures, the portable test confirms the same cross-context signed URL rewrite primitive, which applies to private targets under the same running-task and known-identifier conditions. The PoC was adapted per release only to account for fixture and test-toolchain differences; the exploit primitive is the same signed URL tuple rewrite.

Local test environment:

- Gitea integration test environment.
- Default local Actions artifact storage, not Azure direct upload.
- Existing fixture tasks/artifacts from Gitea's test fixtures.
- The dynamic PoC sets the target task status to `running` before exploiting the URL, matching the vulnerable signed URL requirement.

Run:

```bash
cd /home/kali/gitea/pocs
GITEA_REPO=/home/kali/gitea/repo GOTOOLCHAIN=auto go run ./actions_artifact_v4_cross_task_access_dynamic_poc.go
```

The dynamic PoC writes a temporary integration test into the Gitea checkout, runs only that test, and removes the temporary test afterward.

The test uses:

```text
attacker task: 48
attacker run: 792
attacker job: 193
attacker repository id: 4

target task: 53
target run: 795
target job: 198
target repository: user2/repo2, repository id 2
target artifact: artifact-795-1
crafted attacker artifact: artifact-795-153
```

PoC flow:

1. Create an Actions authorization token for attacker task `48`.
2. Verify the attacker token cannot request a signed URL for target run `795` through the authenticated Twirp API.
3. Create an attacker-controlled V4 artifact named `artifact-795-153`.
4. Upload and finalize that attacker artifact to obtain a legitimate signed URL.
5. Rewrite the signed download URL:

```text
artifactName=artifact-795-1
taskID=53
artifactID=48<attackerArtifactID>
```

6. Send the forged final `GET` without any token and receive the private target artifact from `user2/repo2`.
7. Rewrite the signed upload URL in the same way.
8. Send a forged `PUT ...&comp=appendBlock` with attacker-controlled data.
9. Confirm the target artifact metadata was changed by the forged upload.
10. Open the target run/artifact staging chunk from storage and confirm it contains the attacker-controlled bytes.

Observed output:

```text
source=/home/kali/gitea/repo
ok      code.gitea.io/gitea/tests/integration   9.069s
reproduced: attacker task cannot request a target-run signed URL through the authenticated Twirp method
reproduced: attacker-created V4 signed URL keeps its HMAC after taskID/artifactName/artifactID rewrite
reproduced: unauthenticated final GET returns the URL-selected target artifact instead of attacker content
reproduced: forged UploadArtifact URL writes attacker-controlled bytes into target run/artifact staging storage and changes target artifact metadata
condition=attacker can run a Gitea Actions task and target task/artifact identifiers are known while target task is running
cvss_candidate=CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:N
```

Example version test commands:

```bash
cd /home/kali/gitea/pocs
GITEA_REPO=/home/kali/gitea/version-tests/gitea-v1.26.1 go run ./actions_artifact_v4_cross_task_access_dynamic_poc.go
GITEA_REPO=/home/kali/gitea/version-tests/gitea-v1.25.5 go run ./actions_artifact_v4_cross_task_access_dynamic_poc.go
GITEA_REPO=/home/kali/gitea/version-tests/gitea-v1.24.7 go run ./actions_artifact_v4_cross_task_access_dynamic_poc.go
GITEA_REPO=/home/kali/gitea/version-tests/gitea-v1.23.8 go run ./actions_artifact_v4_cross_task_access_dynamic_poc.go
GITEA_REPO=/home/kali/gitea/version-tests/gitea-v1.22.6 GITEA_TEST_GOTOOLCHAIN=go1.22.12 go run ./actions_artifact_v4_cross_task_access_dynamic_poc.go
```

Some release worktrees require a local `gitea` binary before integration tests run:

```bash
cd /path/to/gitea-release-worktree
go build -tags 'sqlite sqlite_unlock_notify' -o gitea .
```

### Impact

This is a cross-task and cross-repository authorization bypass in Gitea Actions artifact handling.

An attacker who can run an Actions job can obtain a valid V4 artifact signed URL for their own task, rewrite it without invalidating the HMAC, and make the server operate in another running task's context.

Impacted users are Gitea instances with Actions enabled and V4 artifact signed URL handling in use. Private repositories are impacted because the forged signed URL handlers do not re-check repository access after reconstructing task context from URL parameters.

Confirmed impact:

- Confidentiality: read artifacts from a target running task in a private repository.
- Integrity: write attacker-controlled artifact data into the target run/artifact staging storage and mutate target artifact metadata.

This can expose build outputs, logs or packaged artifacts stored as workflow artifacts, and can interfere with in-flight artifact upload staging. Depending on the target upload/finalization flow, it may poison artifact data consumed by later workflow steps, release automation, deployment jobs, or downstream users.

Recommended fix:

- Sign a canonical structured payload, such as JSON/protobuf or length-prefixed fields, instead of concatenating raw values. A versioned payload is preferable, for example `HMAC(version || canonical_payload)`.
- Include and enforce endpoint, expiry, task ID, artifact ID, artifact name, run ID, run attempt ID, repository ID, and owner ID in the signed payload.
- After signature verification, load the artifact by signed `artifactID`.
- Reject the request unless the signed artifact ID, task ID, run ID, run attempt ID, repository ID, owner ID, and artifact name all match.
- Apply artifact-name validation to V4 artifact creation as hardening.

Adding separators alone is not a complete fix if the post-verification code still trusts URL fields and looks up the artifact only by name/run context. Artifact-name validation is also hardening rather than a root-cause fix, because normal valid artifact names can contain digits and separators. The important security property is binding the signed URL to one canonical artifact, task, run, repository, owner, endpoint, and expiry.

## References
- https://github.com/go-gitea/gitea/security/advisories/GHSA-hg5r-vq93-9fv6
- https://nvd.nist.gov/vuln/detail/CVE-2026-58426
- https://github.com/go-gitea/gitea/pull/37707
- https://github.com/go-gitea/gitea/commit/1c2d5e9b03f71dd12d450b2af9a79f2557b50226
- https://blog.gitea.com/release-of-1.26.2
- https://github.com/go-gitea/gitea
- https://github.com/go-gitea/gitea/releases/tag/v1.26.2
