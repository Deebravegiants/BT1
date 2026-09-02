### Title
Webhook `shop` Identity Is Not Bound to the HMAC Signature, Enabling Cross-Tenant Webhook Spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body, then trusts an unauthenticated header to identify which merchant/tenant the event belongs to. Because the tenant-identifying field is never covered by the signature, a party who has received one legitimately-signed webhook for their own shop (any app installer) can resend that exact body with a different shop-domain header and have the app process it as an event belonging to a different tenant.

### Finding Description
`Registry.process` validates a webhook this way: [1](#0-0) 

`Utils::HmacValidator.validate` computes the HMAC exclusively over `to_signable_string`, and `ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw body: [2](#0-1) 

The `shop`, `topic`, and `webhook_id` values used to route and process the event, however, are parsed straight from HTTP headers that are never part of the signed payload: [3](#0-2) 

`Registry.process` then constructs `WebhookMetadata` using `request.shop` — the unauthenticated header — and hands it to the app's handler as the authoritative tenant identity for the event: [4](#0-3) 

The identity binding that should hold is:
`shop authenticated by the signature == shop the app acts on`

But the actual equality enforced by the code is only:
`HMAC(raw_body, client_secret) == received_hmac`

with `shop` sourced from a header that is completely decoupled from that computation. The `client_secret` used to sign every webhook for an app is a single secret shared across *all* merchants who install that app — it is not shop-specific. Consequently, any merchant who installs the app (an "unprivileged internet user" from the perspective of any other tenant of the same app) legitimately receives real webhook bodies with valid HMACs computed by Shopify for their own shop. Nothing in this gem prevents them from replaying that exact `(raw_body, hmac)` pair to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` header with a victim shop's domain — the HMAC still validates (it only checked the body), and `Registry.process` will hand the attacker's data to the handler tagged as belonging to the victim shop.

### Impact Explanation
This breaks the tenant boundary the gem's own documentation claims to enforce ("verify the request did indeed come from Shopify" — see `docs/usage/webhooks.md`), because the request *did* come from Shopify, just for a different (attacker-controlled) shop. Any host application that keys business logic, storage writes, or authorization decisions off `WebhookMetadata#shop` (exactly as the gem's own docs instruct) can be made to apply attacker-supplied webhook content to another merchant's tenant record — a cross-tenant data integrity/access issue reachable by any user who can install the app on their own shop, without needing the `api_secret_key` or any privileged credential.

### Likelihood Explanation
Any registered app user (a low-privilege actor relative to other tenants) can trivially capture one of their own legitimately-delivered webhooks (body + HMAC header) — these are delivered over plain HTTP(S) POST to the app's public webhook endpoint and are visible to the app operator or, if TLS is terminated by infrastructure the attacker also controls (e.g., their own reverse proxy in front of a shared/multi-tenant deployment), to the attacker as well. Replaying it with a modified `shop-domain` header requires only a single HTTP request and no interaction with Shopify's systems or the app's secret.

### Recommendation
Bind the tenant identity to the signed payload instead of trusting an unauthenticated header:
- Include the `shop` domain (and ideally `topic`/`webhook_id`) inside the value that is HMAC-verified, or
- Cross-check the header-supplied `shop` against a shop value embedded in the JSON body/payload where Shopify includes it, rejecting mismatches, or
- At minimum, document prominently that `WebhookMetadata#shop` is unauthenticated and must not be used for authorization decisions without additional verification (e.g., confirming the shop has an active session/webhook registration correlated by `webhook_id`).

### Proof of Concept
1. App merchant "attacker.myshopify.com" installs the app and receives a legitimate webhook: `POST /webhook` with body `{"id":123}`, header `X-Shopify-Shop-Domain: attacker.myshopify.com`, and a valid `X-Shopify-Hmac-Sha256` computed by Shopify using the app's `client_secret`.
2. Attacker replays the identical body and HMAC header to the app's webhook endpoint, but changes `X-Shopify-Shop-Domain` to `victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new(raw_body:, headers:)` parses `shop` as `victim.myshopify.com` [5](#0-4) .
4. `Utils::HmacValidator.validate(request)` succeeds because it only recomputes the HMAC over the unchanged raw body [6](#0-5) .
5. `Registry.process` invokes the app's handler with `WebhookMetadata.new(... shop: "victim.myshopify.com" ...)`, causing the app to process attacker-controlled data under the victim tenant's identity [7](#0-6) .

### Citations

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
