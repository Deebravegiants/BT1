# [H] Gitea: Repository Migration Follows Git HTTP Redirects After URL Allow/Block Validation, Enabling Internal Git Repository Exfiltration

## Summary
Severity: High
Advisory: GHSA-82f7-87hm-852x
CVE: CVE-2026-57894
CWE: CWE-918
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2026-07-21
Source: https://github.com/advisories/GHSA-82f7-87hm-852x
Type: github-advisory

## Affected
- Go: `code.gitea.io/gitea` — affected >=0 <1.27.0

## Details
# Repository Migration Follows Git HTTP Redirects After URL Allow/Block Validation, Enabling Internal Git Repository Exfiltration

## Summary

Gitea validates the user-supplied repository migration URL, but the actual clone and later mirror fetch operations are performed by the Git command-line client without disabling HTTP redirects. Git's default `http.followRedirects=initial` follows the first redirect and then uses the redirected URL as the base for later repository object requests.

This creates a URL-policy bypass, SSRF, and repository exfiltration primitive. A low-privileged authenticated user can submit an allowed public Git URL that redirects the Gitea server to an otherwise blocked or internal Git HTTP(S) endpoint. Local validation confirmed that Git followed a first-hop redirect to `127.0.0.1`, fetched Git objects, and completed the clone; `git -c http.followRedirects=false clone` blocked the same path.

The main impact is internal Git repository exfiltration into an attacker-controlled Gitea repository. Pull mirrors increase risk because scheduled `git fetch --tags` operations can keep following the redirect and collect future internal commits.

This is High severity by default for internet-accessible instances with migrations enabled, and can become Critical where internal repositories contain deploy keys, CI/CD secrets, cloud credentials, Terraform state, kubeconfigs, signing material, or production configuration. Direct unauthenticated exploitation, direct Gitea server RCE, arbitrary `file://` import, and default Actions runner execution are not confirmed.

## Technical Root Cause Analysis

The root cause is a validation/enforcement mismatch across a trust boundary. This should be treated as a product security issue rather than a pure deployment misconfiguration: deployment choices influence reachability and impact, but Gitea applies policy to the originally submitted URL while the Git subprocess is allowed to reach a different effective URL after redirection.

Gitea validates the original migration URL:

- `C:\Users\One\Desktop\gitea_new\gitea\routers\web\repo\migrate.go:180` parses the submitted web migration clone address.
- `C:\Users\One\Desktop\gitea_new\gitea\routers\web\repo\migrate.go:182` calls `migrations.IsMigrateURLAllowed`.
- `C:\Users\One\Desktop\gitea_new\gitea\routers\api\v1\repo\migrate.go:101` parses the submitted API migration clone address.
- `C:\Users\One\Desktop\gitea_new\gitea\routers\api\v1\repo\migrate.go:103` calls `migrations.IsMigrateURLAllowed`.

The URL validator resolves and checks the initially supplied host:

- `C:\Users\One\Desktop\gitea_new\gitea\services\migrations\migrate.go:44` defines `IsMigrateURLAllowed`.
- `C:\Users\One\Desktop\gitea_new\gitea\services\migrations\migrate.go:75` rejects unsupported schemes.
- `C:\Users\One\Desktop\gitea_new\gitea\services\migrations\migrate.go:79` extracts the host.
- `C:\Users\One\Desktop\gitea_new\gitea\services\migrations\migrate.go:85` performs DNS resolution.
- `C:\Users\One\Desktop\gitea_new\gitea\services\migrations\migrate.go:86` enforces the allow/block list on the originally resolved host.

After this validation, the actual repository data transfer is delegated to Git:

- `C:\Users\One\Desktop\gitea_new\gitea\services\repository\migrate.go:93` calls `gitrepo.CloneExternalRepo` with `opts.CloneAddr`.
- `C:\Users\One\Desktop\gitea_new\gitea\modules\gitrepo\clone.go:13` delegates to `git.Clone`.
- `C:\Users\One\Desktop\gitea_new\gitea\modules\git\repo.go:123` constructs a `git clone` command.
- `C:\Users\One\Desktop\gitea_new\gitea\modules\git\repo.go:125` conditionally sets only `http.sslVerify=false`.
- `C:\Users\One\Desktop\gitea_new\gitea\modules\git\repo.go:154` appends the source and destination arguments.

No equivalent network policy is applied to the final URL reached by Git after HTTP redirection. The protected migration HTTP client exists for service-specific migration API calls, but it is not used for the raw Git clone/fetch operation:

- `C:\Users\One\Desktop\gitea_new\gitea\services\migrations\http_client.go:16` defines `NewMigrationHTTPClient`.
- `C:\Users\One\Desktop\gitea_new\gitea\services\migrations\http_client.go:27` applies a host-matching dialer.

That protection does not wrap `git clone` or `git fetch`.

The behavior depends on Git's documented redirect handling. The current Git documentation states that `http.followRedirects=initial` follows the initial request redirect and uses the redirected URL as the base for follow-up requests. The default value is `initial`: https://git-scm.com/docs/git-config#Documentation/git-config.txt-httpfollowRedirects

This means the effective enforcement point is not the same as the actual network sink. Gitea checks `https://attacker.example/repo.git`; Git later retrieves `http://127.0.0.1:PORT/internal.git/...` or another internal target selected by the redirector.

For mirrors, the issue extends beyond initial migration:

- `C:\Users\One\Desktop\gitea_new\gitea\services\repository\migrate.go:177` creates a mirror record when migration is requested as a mirror.
- `C:\Users\One\Desktop\gitea_new\gitea\services\repository\migrate.go:188` stores the sanitized original remote address.
- `C:\Users\One\Desktop\gitea_new\gitea\services\mirror\mirror_pull.go:120` later performs mirror synchronization with `git fetch --tags`.
- `C:\Users\One\Desktop\gitea_new\gitea\services\mirror\mirror_pull.go:126` fetches from the configured remote.

Because the mirror sync path also delegates to Git, a redirecting remote can continue to redirect scheduled fetches into an internal target.

## Affected Assets & Attack Surface

Affected features are URL-based repository migration, API repository migration, pull mirror creation through migration, and scheduled pull mirror synchronization. The relevant entrypoints are `POST /repo/migrate` for signed-in web users (`C:\Users\One\Desktop\gitea_new\gitea\routers\web\web.go:1062`) and `POST /api/v1/repos/migrate` for API-token users (`C:\Users\One\Desktop\gitea_new\gitea\routers\api\v1\api.go:1170`).

Important preconditions are:

- Repository migrations are enabled, which is the default in code and example configuration (`C:\Users\One\Desktop\gitea_new\gitea\modules\setting\repository.go:181`, `C:\Users\One\Desktop\gitea_new\gitea\custom\conf\app.example.ini:1078`).
- The attacker has a low-privileged account or the instance permits self-registration. Default/example service settings do not force registration confirmation by default.
- For persistent exfiltration, pull mirrors must be enabled (`C:\Users\One\Desktop\gitea_new\gitea\modules\setting\mirror.go:20`).
- The Gitea server can reach internal Git HTTP(S) services that the attacker cannot reach directly.

High-value targets include internal Gitea, GitLab, GitHub Enterprise, Bitbucket, cgit, git-http-backend, and static bare Git repositories, especially repositories containing CI/CD definitions, deployment manifests, IaC, credentials, or production configuration.

The key trust boundary is that low-privileged user input influences server-side Git network access. Gitea validates the initially supplied URL, then hands control to a Git subprocess whose redirected destination is not constrained by the same allow/block policy. An attacker can discover exposure by using a controlled redirector, observing outbound Git requests, and testing whether scheduled mirror requests continue to arrive.

## Exploitation Walkthrough

### Scenario 1: One-time internal repository exfiltration

1. The attacker obtains a low-privileged Gitea account. On instances with open registration, this may require only creating a user.
2. The attacker hosts a public HTTP endpoint that appears to be a Git remote, for example `https://attacker.example/public.git`.
3. The attacker configures the endpoint to respond to the initial Git discovery request with an HTTP redirect to an internal target, for example `http://internal-git.company.local/team/private.git/info/refs?service=git-upload-pack`.
4. The attacker submits the public URL to Gitea's repository migration flow.
5. Gitea validates only `attacker.example`, which passes the migration allow/block list.
6. Gitea invokes `git clone --mirror` against the public URL.
7. Git follows the initial redirect and uses the internal Git URL as the base for follow-up object requests.
8. Gitea imports the internal repository contents into the attacker-controlled repository.
9. The attacker browses the imported repository, downloads an archive, clones it, and searches working tree and history for secrets.

### Scenario 2: Persistent exfiltration through pull mirror

1. The attacker performs the same setup but enables mirror migration.
2. Gitea creates a mirror record using the attacker-supplied public URL.
3. On each scheduled mirror synchronization, Gitea runs `git fetch --tags` against the stored remote.
4. The attacker's remote again redirects Git to the internal repository.
5. New internal commits become available in the attacker's Gitea repository after mirror sync.

This materially increases impact because the exposure is not limited to one migration event. The attacker can continue collecting internal commits for as long as the mirror remains enabled and the redirect target remains reachable.

### Scenario 3: Credential-to-RCE chain

This chain is conditional but realistic in DevOps environments.

1. The attacker imports or mirrors an internal repository.
2. The attacker searches the repository and full Git history for secrets:
   - CI variables committed into workflow files.
   - Cloud access keys.
   - Kubernetes kubeconfigs.
   - Terraform state files or backend credentials.
   - Deployment SSH keys.
   - Package registry tokens.
   - Gitea/GitLab/GitHub PATs.
3. The attacker uses the recovered credential to access CI/CD, cloud, container registry, deployment hosts, or orchestration infrastructure.
4. The attacker obtains code execution in a runner, deployment job, Kubernetes workload, cloud function, VM, or production environment.

This is not direct RCE in Gitea from the currently validated evidence. It is a credible post-exploitation chain from server-side internal repository exfiltration to infrastructure compromise.

### Scenario 4: Conditional Gitea Actions runner exposure

Actions-related escalation is configuration-dependent.

Relevant code behavior:

- Actions are detected only when the Actions unit is enabled:
  - `C:\Users\One\Desktop\gitea_new\gitea\services\actions\notifier_helper.go:138`
  - `C:\Users\One\Desktop\gitea_new\gitea\services\actions\notifier_helper.go:146`
- Workflows are detected from commits:
  - `C:\Users\One\Desktop\gitea_new\gitea\services\actions\notifier_helper.go:184`
  - `C:\Users\One\Desktop\gitea_new\gitea\services\actions\notifier_helper.go:186`
- Action runs are created from detected workflows:
  - `C:\Users\One\Desktop\gitea_new\gitea\services\actions\notifier_helper.go:321`
  - `C:\Users\One\Desktop\gitea_new\gitea\services\actions\notifier_helper.go:347`
- Non-fork events do not require approval:
  - `C:\Users\One\Desktop\gitea_new\gitea\services\actions\notifier_helper.go:401`
  - `C:\Users\One\Desktop\gitea_new\gitea\services\actions\notifier_helper.go:405`

Default mirror repository units do not include Actions:

- `C:\Users\One\Desktop\gitea_new\gitea\models\unit\unit.go:88`
- `C:\Users\One\Desktop\gitea_new\gitea\models\unit\unit.go:96`

Therefore, the Actions chain should not be presented as default direct impact. It is a critical conditional chain if an operator enables Actions on migrated/mirrored repositories, customizes default mirror units to include Actions, or manually enables Actions on a mirror. In such cases, redirected repository content containing workflow files may enqueue jobs in a context that is not treated as an untrusted fork pull request.

## Proof-of-Concept & Evidence

### Code evidence

The vulnerable flow is:

1. User-controlled clone URL is accepted by the web or API migration handler.
2. The original URL is validated by `IsMigrateURLAllowed`.
3. The same original URL is passed to `git clone --mirror`.
4. Git follows the initial HTTP redirect by default.
5. Gitea does not revalidate the redirected target.

Key code locations:

- Web migration validation:
  - `C:\Users\One\Desktop\gitea_new\gitea\routers\web\repo\migrate.go:180`
  - `C:\Users\One\Desktop\gitea_new\gitea\routers\web\repo\migrate.go:182`
- API migration validation:
  - `C:\Users\One\Desktop\gitea_new\gitea\routers\api\v1\repo\migrate.go:101`
  - `C:\Users\One\Desktop\gitea_new\gitea\routers\api\v1\repo\migrate.go:103`
- URL policy enforcement:
  - `C:\Users\One\Desktop\gitea_new\gitea\services\migrations\migrate.go:44`
  - `C:\Users\One\Desktop\gitea_new\gitea\services\migrations\migrate.go:85`
  - `C:\Users\One\Desktop\gitea_new\gitea\services\migrations\migrate.go:86`
- Git clone execution:
  - `C:\Users\One\Desktop\gitea_new\gitea\services\repository\migrate.go:93`
  - `C:\Users\One\Desktop\gitea_new\gitea\modules\gitrepo\clone.go:13`
  - `C:\Users\One\Desktop\gitea_new\gitea\modules\git\repo.go:123`
  - `C:\Users\One\Desktop\gitea_new\gitea\modules\git\repo.go:125`
  - `C:\Users\One\Desktop\gitea_new\gitea\modules\git\repo.go:154`
- Mirror persistence and repeated fetch:
  - `C:\Users\One\Desktop\gitea_new\gitea\services\repository\migrate.go:177`
  - `C:\Users\One\Desktop\gitea_new\gitea\services\repository\migrate.go:188`
  - `C:\Users\One\Desktop\gitea_new\gitea\services\mirror\mirror_pull.go:120`
  - `C:\Users\One\Desktop\gitea_new\gitea\services\mirror\mirror_pull.go:126`

### Local validation summary

A local safe PoC was run with two HTTP services:

- Redirector service: represents the attacker-controlled public URL.
- Target service: represents an internal Git HTTP repository on loopback.

Observed behavior:

- `git clone` was invoked against the redirector URL.
- The redirector returned a first-hop HTTP redirect to the internal target URL.
- Git followed the redirect.
- The internal target received Git requests for:
  - `/info/refs`
  - `/HEAD`
  - object paths required for clone completion
- The clone completed successfully.
- The cloned repository contained the expected file content from the internal target repository.

The local PoC result showed:

```text
code: 0
redirector hit count: 1
target hit count: 5
cloned content: "internal repo data via redirected git clone"
```

Mirror fetch behavior was also validated locally:

- A bare mirror remote was configured to point at the redirector URL.
- `git fetch --tags origin` followed the redirect into the internal target.
- The target received object requests.
- The mirror fetched the expected branch reference successfully.

The mirror PoC result showed:

```text
code: 0
target object requests observed: 5
hasFetchedBranchRef: true
```

Mitigation behavior was validated locally:

- The same clone was run with `git -c http.followRedirects=false clone`.
- Git failed on the redirect with an HTTP 302 error.
- This confirms that disabling Git HTTP redirects blocks the validated redirect SSRF path.

The failed mitigation test behavior was:

```text
fatal: unable to access '<redirector-url>': The requested URL returned error: 302
```

Negative validation:

- An HTTP redirect to `file://` was attempted.
- Git refused the redirected local-file protocol with `Protocol "file" disabled (in redirect)`.
- Based on this validation, this report does not claim arbitrary local filesystem read or local repository import through `file://` redirection.

Validation scope:

- The local PoC validates the security-critical network sink used by the Gitea migration path: Git clone/fetch follows the redirect and retrieves repository objects from the redirected internal target.
- The source review validates that Gitea's migration handlers pass the validated clone URL into that Git clone/fetch path without disabling HTTP redirects.
- A full disposable Gitea UI/API end-to-end import proof was not executed as part of this report. If additional assurance is required before external submission, the highest-value next validation step is to run a temporary Gitea instance, create a low-privileged user, submit the redirector URL through `POST /repo/migrate` or `POST /api/v1/repos/migrate`, and confirm that the resulting attacker-owned Gitea repository contains the internal repository content. For mirror mode, add a new commit to the internal target and confirm a later mirror sync imports it.

## Impact Assessment

Confirmed impact is server-side Git network access to a redirected destination, resulting in internal Git repository import when the redirected target is reachable from the Gitea server. This can expose private source code, full Git history, deleted secrets, internal architecture, deployment pipelines, service names, and future commits if pull mirrors continue syncing.

The highest-risk secondary impact is secret extraction. Internal repositories often contain CI/CD definitions, deployment scripts, kubeconfigs, Terraform state, cloud keys, registry tokens, package publishing tokens, PATs, SSH deploy keys, webhook secrets, and historical credentials. Exposure of these materials can escalate to CI/CD compromise, cloud compromise, production access, or supply-chain compromise.

Direct Gitea server RCE is not confirmed. The clone path uses `git clone --mirror`, remote Git hooks are not executed by a normal clone, local validation showed Git rejects `file://` redirects, and the reviewed command construction does not show obvious shell injection. Indirect RCE remains plausible through stolen CI/CD, cloud, deployment, package, or Actions runner credentials.

Incident responders should treat exploitation as potential source-code and secret disclosure, not just SSRF probing. Recommended triage is to review recently migrated repositories and mirrors, identify unusual migration sources or redirector domains, inspect Gitea and egress logs around migration/mirror sync times, secret-scan affected full histories, rotate exposed credentials, and remove malicious mirror configurations.

## Remediation Guidance

Disable Git HTTP redirects for migration clone and mirror fetch operations unless every redirect hop is explicitly revalidated under the same migration allow/block policy.

Recommended immediate code changes:

- Invoke migration clone as `git -c http.followRedirects=false clone ...` (`C:\Users\One\Desktop\gitea_new\gitea\modules\git\repo.go:123`).
- Invoke pull mirror fetch as `git -c http.followRedirects=false fetch ...` (`C:\Users\One\Desktop\gitea_new\gitea\services\mirror\mirror_pull.go:122`).

Local mitigation testing confirmed that `http.followRedirects=false` prevents the redirect-based clone from succeeding. If redirect support is required for compatibility, Gitea should follow redirects in controlled code, validate each hop against the migration network policy, and then invoke Git with redirects disabled.

Defense in depth:

- Enforce egress restrictions for the Gitea process/container.
- Block outbound access to loopback, RFC1918, link-local, multicast, metadata-service ranges, and internal Git services unless explicitly required.
- Disable repository migrations and new pull mirrors where not operationally required.
- Restrict migration access to trusted users; disable public self-registration or require manual approval.
- Require authentication on internal Git HTTP endpoints even when they are network-internal.

## Risk Classification

Severity: High by default for internet-accessible instances with repository migrations enabled; Critical in environments where Gitea can reach sensitive internal Git services containing secrets, deploy keys, CI/CD credentials, cloud credentials, or production configuration.

Critical escalation conditions:

Critical escalation conditions include sensitive internal Git reachability, weak egress controls, repositories containing production or CI/CD secrets, enabled pull mirrors that continue syncing future commits, or configurations where imported workflow content can reach shared/self-hosted Actions runners.

Not confirmed:

Direct unauthenticated exploitation, direct Gitea server RCE from the migration clone path, arbitrary local filesystem read via `file://` redirect, and default Actions runner execution from mirror sync without configuration changes.

## References
- https://github.com/go-gitea/gitea/security/advisories/GHSA-82f7-87hm-852x
- https://github.com/go-gitea/gitea
- https://github.com/go-gitea/gitea/releases/tag/v1.27.0
