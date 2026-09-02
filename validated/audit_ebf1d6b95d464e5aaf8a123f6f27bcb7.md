## Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing cross-tenant shop spoofing via webhook replay - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes and validates the webhook HMAC over the raw request body only, while `topic`, `shop`, `webhook_id`, and `api_version` are read straight from HTTP headers that are never part of the signed payload. The gem then hands `request.shop` straight to the app's webhook handler as if it were an authenticated value. An attacker who can obtain one validly-signed webhook body (trivially, by owning any Shopify store and triggering a webhook on it) can replay that exact body with a forged `shop-domain` header pointing at a victim shop, and the library will accept it as valid and report it as belonging to the victim shop.

### Finding Description
`Request#to_signable_string` only returns the raw body: [1](#0-0) 

`HmacValidator.validate` computes the signature exclusively over `verifiable_query.to_signable_string`: [2](#0-1) 

Meanwhile `shop`, `topic`, `webhook_id`, and `api_version` are pulled unauthenticated from headers: [3](#0-2) 

`Registry.process` validates only the body-derived HMAC, then forwards `request.shop` (an unsigned header value) directly into `WebhookMetadata`, which is delivered to the app's handler as the authoritative shop identity for that payload: [4](#0-3) 

The identity binding that should hold is:
`shop asserted by the HMAC-protected payload == shop delivered to the handler`

but what is actually checked is:
`HMAC(raw_body) is valid` AND (separately, unauthenticated) `shop header == whatever the request happened to carry`

These are not the same value, and the header is never cross-checked against anything covered by the signature. The gem's own documentation instructs app authors to trust `data.shop` as "The shop domain of the webhook": [5](#0-4) 

### Impact Explanation
Because the body itself typically doesn't encode which shop it came from (Shopify's payload for `orders/create`, `customers/data_request`, etc. does not embed the owning shop domain in a way the gem checks), any attacker who legitimately owns a Shopify store can:
1. Install the target app on their own (attacker-owned) store, so Shopify signs real webhooks to the app's endpoint using the app's `api_secret_key` — no privileged credential of the victim or the app is required, since the attacker triggers this on their own tenant.
2. Capture the resulting `raw_body` + `X-Shopify-Hmac-Sha256` value from a webhook of their choosing.
3. Replay the identical body/HMAC pair to the app's webhook endpoint while substituting `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `Utils::HmacValidator.validate` succeeds (only the body is checked), and the handler receives `data.shop == "victim-shop.myshopify.com"` with attacker-supplied body content.

Any host application that keys tenant-scoped operations off `data.shop` (as the library's own documentation instructs) will apply attacker-controlled webhook data to the victim shop's tenant context — a cross-tenant data-integrity break attributable to this gem's identity binding, not to host misuse of an undocumented feature.

### Likelihood Explanation
Obtaining one validly-HMAC'd body/signature pair requires nothing more than installing the target app on any store the attacker controls — something any internet user can freely do for public apps — and no possession of the app's `client_secret`/`api_secret_key` is needed. The replay itself is a single crafted HTTP POST with a modified header. This is a low-effort, unprivileged, repeatable attack path.

### Recommendation
Include `shop`, `topic`, `webhook_id`, and `api_version` in the signed material verified by `HmacValidator` (mirroring what Shopify actually authenticates end-to-end, or at minimum cross-validating the header-derived shop against the session/tenant context the app already has for that HMAC secret), or explicitly document that `shop-domain` and other webhook headers are NOT authenticated by the HMAC and must not be used by host applications as a tenant-identity signal without additional verification (e.g., correlating against `Context.active_session`/an existing merchant record established via OAuth).

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker.myshopify.com` and triggers a webhook (e.g. `orders/create`) with attacker-controlled body content.
2. Attacker captures the raw POST: body `B`, and header `X-Shopify-Hmac-Sha256: H` (valid, computed by Shopify using the app's real secret).
3. Attacker sends a new POST to the same webhook endpoint with the same body `B` and header `H`, but sets `X-Shopify-Shop-Domain: victim.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` accepts the request:
   - `Utils::HmacValidator.validate(request)` → `true` (only `B` is hashed).
   - `handler.handle(data: WebhookMetadata.new(shop: "victim.myshopify.com", body: parsed(B), ...))` is invoked, delivering attacker data tagged as belonging to `victim.myshopify.com`.

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

**File:** docs/usage/webhooks.md (L12-17)
```markdown
`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook
```
