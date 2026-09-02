### Title
Webhook `shop-domain` header is trusted for tenant identity but is not covered by the HMAC signature - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature only over the raw request body, while the `shop`, `topic`, `api_version`, and `webhook_id` values used by application code to identify *which merchant* the event belongs to are taken from unauthenticated HTTP headers that are never included in the signed content.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

and `Request#shop` simply reads the `shopify-shop-domain`/`x-shopify-shop-domain` header verbatim, with no cryptographic binding to the body or the HMAC: [2](#0-1) 

`Utils::HmacValidator.validate` verifies the signature purely against `verifiable_query.to_signable_string` (i.e. the raw body) using the app's shared `api_secret_key`: [3](#0-2) 

`Registry.process` then trusts `request.shop` — the unauthenticated header value — as the tenant identity forwarded to the app's handler, immediately after the HMAC check passes: [4](#0-3) 

The identity binding that should hold is: `shop authenticated by the HMAC == shop trusted for tenant routing`. Because `api_secret_key` (the app's single `client_secret`) is identical for every shop that installs the app, and the header carrying the shop identity is excluded from the signed bytes, the HMAC only proves "this body was produced by Shopify for *some* installation of this app" — not "this body belongs to *this* shop-domain header". This is the same class of bug as the reported M-9 issue: a value that is acted upon (`shop`) is not bound to the value that is cryptographically verified (`raw_body`).

### Impact Explanation
If an attacker can cause a genuinely Shopify-signed webhook body/HMAC pair to be replayed (or forwarded) to the app's shared webhook endpoint with a different `shop-domain` header, `HmacValidator.validate` still returns `true` (it never inspects headers), and `Registry.process` hands the handler a `WebhookMetadata` claiming the event belongs to an arbitrary victim shop. Any host application that uses `request.shop`/`data.shop` to look up per-tenant state (the documented, intended use per `docs/usage/webhooks.md`) can be tricked into attributing another merchant's data/actions to the wrong tenant — a cross-tenant identity confusion rooted entirely in this gem's `Request`/`Registry` implementation.

### Likelihood Explanation
Exploitation requires the attacker to obtain a valid `(raw_body, hmac)` pair that was genuinely signed by Shopify (e.g., from their own installed shop's webhook traffic) and cause it to be re-delivered with a forged header to the shared endpoint. This is a webhook-header-spoofing primitive that depends on how/where the (body, hmac) pair can be captured and replayed in a given deployment; it does not require possession of `api_secret_key` or TLS interception, but does require some avenue to resubmit a captured payload to the endpoint.

### Recommendation
Include the shop-domain (and ideally topic/webhook_id) in the value that is HMAC-verified, or otherwise cryptographically bind the header-derived identity to the signed payload before exposing it via `Request#shop`/`WebhookMetadata`, e.g. by having `to_signable_string` incorporate the relevant headers, or by validating that `shop` is a value the app previously registered a webhook for the corresponding topic against a per-shop secret/session, not just any shop string in the header.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com` and triggers a webhook event (e.g., `orders/create`), producing a body `B` and Shopify-computed `hmac = HMAC-SHA256(client_secret, B)`.
2. Attacker captures this genuine `(B, hmac)` pair (e.g., via their own logging/proxy in front of their receiving endpoint, or any means short of possessing `client_secret`).
3. Attacker resubmits `POST /webhook` to the shared app endpoint with the same raw body `B` and the same `x-shopify-hmac-sha256` header, but sets `x-shopify-shop-domain: victim.myshopify.com`.
4. `Utils::HmacValidator.validate` succeeds because it only checks `B` against `client_secret`; `Registry.process` calls the handler with `WebhookMetadata.new(... shop: "victim.myshopify.com" ...)`, causing the app to process attacker-controlled data under the victim's tenant identity.

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
