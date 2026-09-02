Line 125 of `docs/usage/webhooks.md` explicitly states that `Registry.process` "will verify the request did indeed come from Shopify" — this is the gem's documented contract, and the `data.shop` field is documented as "The shop domain of the webhook" with no caveat that it is unverified. This confirms the finding is a genuine gap in the gem's own documented guarantee, not something requiring the host app to ignore documented behavior.

### Title
Webhook `shop` identity is not bound to the HMAC signature, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` verifies only that the raw request body matches its HMAC signature, then trusts the unauthenticated `shop-domain` header as the tenant identity passed to the app's webhook handler. Any party who can obtain one validly-signed webhook body (e.g., by installing the app on their own store) can replay that exact body/HMAC pair while substituting an arbitrary `shop-domain` header value, since that header is never part of the signed bytes.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 
and `#shop` is read directly from an unauthenticated header with no cross-check against the signed content: [2](#0-1) 

`Registry.process` validates only the HMAC of that signable string, then immediately forwards `request.shop` to the app's handler as the trusted tenant identity: [3](#0-2) 

`HmacValidator.validate` confirms this — it only ever hashes `verifiable_query.to_signable_string` (i.e., the raw body) against the secret, never the header set: [4](#0-3) 

This is exactly the bug class from the external report: a field ("shop") that is acted upon by the application (used as the tenant key in `WebhookMetadata`) is not covered by the HMAC that is supposed to authenticate the request. The equality that should hold — `shop-header == shop bound inside the HMAC-signed payload` — never actually holds, because the HMAC only binds the JSON body bytes, and the body sent by Shopify for a given topic doesn't itself assert which shop it belongs to independent of the header.

The gem's own documentation asserts that `Registry.process` "will verify the request did indeed come from Shopify," and describes `data.shop` as simply "The shop domain of the webhook," giving no indication to implementers that this value is attacker-controllable metadata requiring independent verification.

### Impact Explanation
An attacker who legitimately installs the target app on their own (attacker-controlled) shop receives real webhook deliveries from Shopify with valid HMAC signatures computed using the app's shared `client_secret`. Because that secret is identical for every shop the app is installed on, the attacker can capture one such valid `(body, hmac)` pair and resend it to the app's webhook endpoint with the `x-shopify-shop-domain` (or `shopify-shop-domain`) header rewritten to name a victim shop. `HmacValidator.validate` will still return `true`, and `Registry.process` will invoke the handler with `WebhookMetadata#shop` set to the victim's domain. Any host application that uses `data.shop` from the gem to key data writes, deduplicate work, or otherwise act as if the shop identity is authenticated (which the gem's docs encourage) can be made to attribute attacker-controlled webhook content to another tenant — a cross-tenant data-integrity/isolation break.

### Likelihood Explanation
Likelihood is High for a straightforward form of it (spoofing your own webhook body under a different shop label), because it requires nothing beyond installing the app once (an ordinary, unprivileged action available to anyone) and issuing one crafted HTTP POST — no access token, `api_secret_key`, or elevated privilege is needed.

### Recommendation
Include the `shop-domain` (and ideally `topic`/`webhook-id`) header values in the HMAC-signed material that `HmacValidator` checks, e.g., by computing the signature over a canonical string that concatenates the raw body with these header values, so that a signature valid for one shop/topic cannot be replayed for another. At minimum, document prominently that `data.shop` must be cross-checked by the host application against a shop that has a legitimately registered webhook/session before being trusted for any tenant-scoped action.

### Proof of Concept
1. Install the target Shopify app on attacker-owned shop `attacker.myshopify.com`; Shopify sends a legitimate webhook POST with body `B` and header `x-shopify-hmac-sha256: H`, where `H = HMAC-SHA256(client_secret, B)`, and `x-shopify-shop-domain: attacker.myshopify.com`.
2. Capture `(B, H)`.
3. Send a new POST to the app's webhook endpoint with the same body `B` and same `x-shopify-hmac-sha256: H`, but with `x-shopify-shop-domain: victim.myshopify.com`.
4. `ShopifyAPI::Utils::HmacValidator.validate` recomputes `HMAC-SHA256(client_secret, B)` — unaffected by the header change — and returns `true` (see `lib/shopify_api/utils/hmac_validator.rb` lines 26-31 and `lib/shopify_api/webhooks/request.rb` lines 35-38).
5. `ShopifyAPI::Webhooks::Registry.process` calls the app's handler with `WebhookMetadata.new(..., shop: "victim.myshopify.com", ...)` (`lib/shopify_api/webhooks/registry.rb` lines 198-199), even though the body and signature originated from the attacker's own shop.

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
