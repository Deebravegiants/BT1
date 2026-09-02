## Title
Webhook `shop-domain` header is not covered by the HMAC signature, enabling cross-tenant webhook forgery - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, so the HMAC that `HmacValidator` verifies binds solely to the body bytes. The `shop`, `topic`, `webhook_id`, and `api_version` values are all pulled straight from HTTP headers that are excluded from the signed content, yet `Registry.process` trusts `request.shop` as the authoritative tenant identity when dispatching the webhook to the app's handler.

### Finding Description
`Request#to_signable_string` is defined as: [1](#0-0) 

and `shop` is read from an unauthenticated header: [2](#0-1) 

`HmacValidator.validate` computes the signature purely from `to_signable_string`, i.e. `@raw_body`: [3](#0-2) 

`Registry.process` only checks that this body-only HMAC is valid, then dispatches using `request.shop` (the unauthenticated header) as the tenant identifier passed to the app's handler: [4](#0-3) 

The equality the gem is supposed to enforce is:
`shop authenticated by HMAC == shop acted upon by the handler`

But in reality the HMAC only proves:
`body bytes == body bytes signed by Shopify with api_secret_key`

Because the same `api_secret_key` is used for every shop that installs the app, any merchant (an "unprivileged" tenant relative to other merchants of the same app) can legitimately trigger a webhook to their own shop, capture the `raw_body` + valid `hmac-sha256` header, then replay that exact body/HMAC pair to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` header (and optionally topic/webhook-id) for a victim shop domain. `HmacValidator.validate` still returns `true` because it never inspects the headers, and `Registry.process` forwards the forged `shop` value straight to the registered handler as `WebhookMetadata#shop`.

### Impact Explanation
This breaks the tenant boundary the gem is expected to preserve: a request that only proves "the body came from Shopify for *some* shop" is treated as proof it came from *any* attacker-chosen shop. Any app handler logic keyed off `WebhookMetadata#shop` (e.g., looking up/creating shop records, entitlements, mandatory GDPR redaction handlers, billing state) can be invoked and populated under a victim shop's identity by an attacker who merely has a store where the app is installed — a cross-tenant identity confusion, matching the report's bug class of "an action performed based on a field not covered by the integrity check."

### Likelihood Explanation
Any merchant who installs the app once obtains a valid `(body, hmac)` pair for a chosen topic without needing the `api_secret_key`, TLS interception, or privileged access — they simply observe their own store's webhook deliveries (or trigger events that fire predictable-body webhooks, e.g., `shop/redact`, `customers/data_request`) and POST the captured payload to the app's public webhook endpoint with a spoofed `shop-domain` header. No credential or account privilege beyond "app installed on some shop" is required.

### Recommendation
Bind the shop (and ideally topic/webhook-id) into the signed content, or otherwise verify that `request.shop` corresponds to a shop session/installation the app actually owns before trusting it. At minimum, `HmacValidator`/`Registry.process` should require the caller to supply the expected shop (from server-side installation records) and reject processing when it doesn't match `request.shop`, rather than trusting the header value implicitly once the body-only HMAC passes.

### Proof of Concept
1. Attacker installs the app on `attacker.myshopify.com`.
2. Shopify sends a webhook to the app with headers `X-Shopify-Shop-Domain: attacker.myshopify.com`, `X-Shopify-Topic: customers/data_request`, body `B`, and `X-Shopify-Hmac-Sha256: H` (computed over `B` with the app's shared `api_secret_key`).
3. Attacker captures `(B, H)` and replays it directly to the app's public webhook endpoint, but with the header rewritten to `X-Shopify-Shop-Domain: victim.myshopify.com`.
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC over `B` only — passes.
5. `handler.handle` is invoked with `WebhookMetadata.new(topic: ..., shop: "victim.myshopify.com", body: parsed(B), ...)`, causing the app to act as if `victim.myshopify.com` sent this webhook, even though the payload and topic were entirely attacker-controlled/replayed.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
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
