## Title
Webhook Shop-Domain Header Not Bound to HMAC Signature Enables Cross-Tenant Webhook Spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
The library's webhook processing validates an inbound webhook's authenticity by computing an HMAC over the **raw request body only**. The `shop` (and `topic`, `api_version`, `webhook_id`) values that identify *which tenant* the webhook belongs to are read from unauthenticated HTTP headers and are never included in the signed payload. Because Shopify webhook HMACs are computed with the app's single `client_secret` (shared across every shop that has the app installed), any shop that has installed the app can capture one of its own legitimately-signed webhook deliveries and replay it to the app's public webhook endpoint with the `X-Shopify-Shop-Domain` header changed to a victim shop, producing a request that passes `HmacValidator.validate` while being attributed to the wrong tenant.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop`, `topic`, `api_version`, and `webhook_id` are all pulled straight from headers with no cryptographic binding to the signature: [2](#0-1) 

`Registry.process` validates the request purely via `HmacValidator.validate(request)`, and then constructs `WebhookMetadata` — including `shop: request.shop` — directly from the unauthenticated header value, passing it straight to the host application's handler: [3](#0-2) 

`HmacValidator.validate` computes the signature purely from `verifiable_query.to_signable_string`, which for a webhook `Request` is the raw body — the shop-domain header is not part of what is signed: [4](#0-3) 

The broken identity binding is:
```
HMAC_valid(raw_body, client_secret) == true
       ⇏
request.shop == the shop that actually generated raw_body
```
Because Shopify computes webhook HMACs using the app-level `client_secret` — the **same secret for every shop** that installs the app — a webhook that Shop A legitimately receives from Shopify carries an HMAC that is equally "valid" no matter which shop-domain header accompanies it. Nothing in the signed material ties the payload to Shop A specifically. An attacker who controls Shop A (an ordinary, unprivileged merchant installing the app — no access to `api_secret_key` needed) can:
1. Install the app on their own shop and trigger/capture a legitimate webhook delivery (raw body + `X-Shopify-Hmac-Sha256` header) that Shopify sends them.
2. Replay that exact body/HMAC pair to the app's public webhook endpoint, but substitute `X-Shopify-Shop-Domain` with a victim shop's domain (and optionally change `X-Shopify-Topic`/`webhook-id`, which are equally unauthenticated).
3. `HmacValidator.validate` still succeeds because it only checks the body against the shared secret, and `Registry.process` forwards `shop: <victim-shop>` to the host application's webhook handler as if it were an authentic event for that tenant.

Depending on how the host app's handler code trusts `WebhookMetadata#shop` (e.g., to look up/update per-shop records, mark orders paid, sync product data, or disable/enable features per shop), this allows an unprivileged internet user to inject falsified events attributed to a store they do not own — a cross-tenant identity confusion rooted entirely in this gem's `Utils::HmacValidator`/`Webhooks::Request` design, not in host misuse.

### Impact Explanation
This crosses a tenant boundary: an attacker who is a legitimate (if malicious) installer of the app on their own store can forge webhook events that the library will vouch for as originating from a different, victim shop, without needing the victim's or the app's credentials. This matches the "cross-tenant access" Critical impact criterion, since any host application relying on `Registry.process`/`WebhookMetadata#shop` for per-tenant data handling inherits the spoofing.

### Likelihood Explanation
Exploitation only requires: (1) installing the target app on an attacker-controlled store (a normal, unprivileged action any merchant can take), (2) capturing one legitimately delivered webhook (trivial — just log inbound HTTP requests at the attacker's own endpoint or capture retries), and (3) replaying it with a modified header to the app's already-public webhook URL. No secrets, tokens, or elevated access are required, making this readily reachable by any external actor able to install the target Shopify app.

### Recommendation
- Bind the tenant-identifying values to the signed material, or otherwise cryptographically verify that `shop`/`topic`/`webhook_id` correspond to the entity for which the HMAC was issued (e.g., by cross-checking `request.shop` against a session or app-installation record before invoking the handler, not merely trusting the header).
- At minimum, document prominently that `WebhookMetadata#shop` is derived from an unauthenticated header and must be independently verified against known/installed shops before being used to key any tenant-sensitive operation.
- Consider incorporating the `shop-domain` header into `to_signable_string` if a scheme can be devised that remains compatible with Shopify's actual signing behavior, or reject payloads for shops that are not part of the app's registered installation set as an additional binding check inside `Registry.process`.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com`.
2. Attacker triggers any webhook topic the app subscribes to (e.g., `orders/create`) on their own store and captures the raw POST body `B` and header `X-Shopify-Hmac-Sha256: H`, where `H = HMAC-SHA256(client_secret, B)`.
3. Attacker sends a new HTTP POST to the app's public webhook endpoint with:
   - Body: `B` (unchanged)
   - `X-Shopify-Hmac-Sha256: H` (unchanged, still valid since it only signs `B`)
   - `X-Shopify-Shop-Domain: victim-shop.myshopify.com` (forged)
   - `X-Shopify-Topic`, `X-Shopify-Webhook-Id` optionally forged as well.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC-SHA256(client_secret, B)` and matches `H` — validation succeeds.
5. The registered handler is invoked with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)`, causing the host application to process/store data as if it were a genuine event from `victim-shop.myshopify.com`.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-33)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end

      sig { returns(String) }
      def api_version
        T.cast(shopify_header("api-version"), String)
      end

      sig { returns(String) }
      def webhook_id
        T.cast(shopify_header("webhook-id"), String)
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end
```

**File:** lib/shopify_api/webhooks/registry.rb (L188-200)
```ruby
        sig { params(request: Request).void }
        def process(request)
          raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)

          handler = @registry[request.topic]&.handler

          unless handler
            raise Errors::NoWebhookHandler, "No webhook handler found for topic: #{request.topic}."
          end

          handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
            body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
        end
```

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
