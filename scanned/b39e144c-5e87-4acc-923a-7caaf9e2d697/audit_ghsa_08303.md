# [M] Flowise: Cross-Workspace Chatflow Disclosure via chatflows/apikey Endpoint Returns All Unprotected Chatflows

## Summary
Severity: Medium
Advisory: GHSA-c2c9-mfw7-p8hw
CVE: CVE-2026-56268
CWE: CWE-863
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-05-20
Source: https://github.com/advisories/GHSA-c2c9-mfw7-p8hw
Type: github-advisory

## Affected
- npm: `flowise` — affected >=0 <3.1.2

## Details
## Summary

The `/api/v1/chatflows/apikey/:apikey` endpoint (whitelisted, accessible with API key auth only) returns all chatflows bound to the provided API key AND all chatflows across the entire system that have no API key assigned. This crosses workspace boundaries, allowing a user in Workspace A who has a valid API key to read the full configuration (including flowData, chatbotConfig, system prompts, and node configurations) of chatflows from Workspace B, Workspace C, and all other workspaces, as long as those chatflows have no API key assigned.

## Details

The controller at `packages/server/src/controllers/chatflows/index.ts:90-107` validates the API key and calls the service:

```typescript
const getChatflowByApiKey = async (req: Request, res: Response, next: NextFunction) => {
    try {
        const apikey = await apiKeyService.getApiKey(req.params.apikey)
        if (\!apikey) {
            return res.status(401).send("Unauthorized")
        }
        const apiResponse = await chatflowsService.getChatflowByApiKey(apikey.id, req.query.keyonly)
        return res.json(apiResponse)  // Returns full chatflow objects with flowData
    } catch (error) {
        next(error)
    }
}
```

The service at `packages/server/src/services/chatflows/index.ts:223-245` builds the database query:

```typescript
const getChatflowByApiKey = async (apiKeyId: string, keyonly?: unknown): Promise<any> => {
    const appServer = getRunningExpressApp()
    let query = appServer.AppDataSource.getRepository(ChatFlow)
        .createQueryBuilder("cf")
        .where("cf.apikeyid = :apikeyid", { apikeyid: apiKeyId })
    if (keyonly === undefined) {
        // When keyonly is not set (default), also return ALL chatflows with no API key
        query = query.orWhere("cf.apikeyid IS NULL").orWhere("cf.apikeyid = ''")
    }
    const dbResponse = await query.orderBy("cf.name", "ASC").getMany()
    return dbResponse  // Returns full ChatFlow entities including flowData
}
```

When `keyonly` is not provided as a query parameter (which is the default case), the query expands to include:
- All chatflows bound to the provided API key (same workspace, expected behavior)
- ALL chatflows with `apikeyid IS NULL` (any workspace, no workspace filter)
- ALL chatflows with empty `apikeyid` (any workspace, no workspace filter)

There is NO `workspaceId` filter in this query. The response includes the full `ChatFlow` entity, which contains:
- `flowData` - the complete workflow graph including system prompts, model names, internal URLs, custom code
- `chatbotConfig` - chatbot configuration including allowed origins
- `apiConfig` - API configuration and override settings
- `textToSpeech` / `speechToText` - TTS/STT configuration including credential IDs
- `analytic` - analytics configuration

## PoC

```bash
# Step 1: Attacker has a valid API key for Workspace A
API_KEY="<attacker-workspace-a-api-key>"

# Step 2: Query the chatflows/apikey endpoint WITHOUT keyonly parameter
# Returns the attacker chatflows PLUS all chatflows without API keys from ALL workspaces
curl -s "http://localhost:3000/api/v1/chatflows/apikey/" | jq ".[].workspaceId"

# Step 3: With keyonly parameter, only chatflows bound to the API key are returned
curl -s "http://localhost:3000/api/v1/chatflows/apikey/?keyonly=true" | jq ".[].workspaceId"
```

## Impact

- **Cross-Workspace Information Disclosure**: A user in any workspace can read the full configuration of chatflows from all other workspaces that do not have an API key assigned. This breaks workspace isolation.
- **Intellectual Property Exposure**: System prompts, custom function code, and workflow architecture of chatflows from other workspaces/organizations are exposed.
- **Credential Reference Leakage**: The `textToSpeech` and `speechToText` fields include credential IDs, which can be abused via the TTS generate endpoint.
- **Amplified by Default**: Most chatflows are created without an API key assigned (API keys are opt-in), so the majority of chatflows in a multi-workspace deployment are affected.

## Recommended Fix

Add workspace scoping to the `getChatflowByApiKey` query by passing the API key workspace ID and filtering the OR clause:

```typescript
// packages/server/src/services/chatflows/index.ts
const getChatflowByApiKey = async (apiKeyId: string, keyonly?: unknown, workspaceId?: string): Promise<any> => {
    const appServer = getRunningExpressApp()
    let query = appServer.AppDataSource.getRepository(ChatFlow)
        .createQueryBuilder("cf")
        .where("cf.apikeyid = :apikeyid", { apikeyid: apiKeyId })
    if (keyonly === undefined && workspaceId) {
        // Only include unprotected chatflows from the SAME workspace
        query = query.orWhere(
            "(cf.apikeyid IS NULL OR cf.apikeyid = :empty) AND cf.workspaceId = :workspaceId",
            { empty: "", workspaceId }
        )
    }
    const dbResponse = await query.orderBy("cf.name", "ASC").getMany()
    return dbResponse
}
```

## References
- https://github.com/FlowiseAI/Flowise/security/advisories/GHSA-c2c9-mfw7-p8hw
- https://nvd.nist.gov/vuln/detail/CVE-2026-56268
- https://github.com/FlowiseAI/Flowise
- https://www.vulncheck.com/advisories/flowise-cross-workspace-information-disclosure-via-chatflows-apikey-endpoint
