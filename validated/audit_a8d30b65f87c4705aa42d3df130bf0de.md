## Title
Webhook `shop-domain`, `topic`, `webhook-id` and `api-version` headers are not covered by the HMAC, enabling cross-tenant webhook forgery - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant-identifying fields (`shop`, `topic`, `webhook_id`, `api_version`) exclusively from HTTP headers, while the HMAC signature that `ShopifyAPI::Utils::HmacValidator` verifies is computed only over the raw request body. Anyone in possession of a single valid `(body, hmac)` pair — which is trivially obtained from any shop that legitimately triggers a webhook, including one the attacker controls — can replay that exact body/HMAC to the app's webhook endpoint while substituting an arbitrary `shop-domain` header. The signature still validates because it never bound the shop identity, allowing the request to be processed as if it originated from a different (victim) tenant.

### Finding Description
`Request#to_signable_string` returns only the raw body, and `Request#hmac` simply reads the `hmac-sha256` header without binding it to any other header: [1](#0-0) [2](#0-1) 

`HmacValidator.validate` computes the signature purely from `verifiable_query.to_signable_string` (the body) and compares it to the header-supplied `hmac`: [3](#0-2) 

`Registry.process` then trusts `request.shop`, `request.topic`, and `request.webhook_id` — none of which are covered by the HMAC — as the tenant/topic identity forwarded to the app's handler: [4](#0-3) 

The binding that should hold is:
`hmac == HMAC(secret, body || shop || topic || webhook_id || api_version)`

but the actual implementation only enforces:
`hmac == HMAC(secret, body)`

Since `shop`, `topic`, `webhook_id`, and `api_version` are parsed from unauthenticated headers, an attacker who owns/controls one shop where the app is installed can capture a legitimate `(body, hmac)` webhook delivery from their own shop, then resend that identical body and HMAC to the app's webhook endpoint with the `shop-domain` header rewritten to any other shop that also has the app installed. The signature check passes because it was never a function of the shop header, and the app's handler receives `WebhookMetadata` attributing the (attacker-controlled) body to the victim shop.

### Impact Explanation
This breaks the tenant-identity binding between the cryptographically verified payload and the shop it's attributed to. An attacker who is a legitimate but low-privilege user of the app (or who can otherwise obtain one valid signed webhook, e.g. by installing a trial/dev store) can inject data into another merchant's tenant context, causing the host application to process attacker-chosen data under a victim shop's identity — cross-tenant contamination/access via the webhook processing pipeline, which is the "Critical - cross-tenant access" category.

### Likelihood Explanation
Likelihood is moderate-to-high for any app that (a) allows self-serve installs (e.g. via the Shopify App Store, meaning the attacker can install the app on a shop they control) and (b) has at least one webhook topic that produces attacker-influenceable body content (e.g. `orders/create`, `products/update`, `carts/update`), since Shopify signs webhooks with the app's own `client_secret`/api_secret_key for every installed shop identically — the attacker just needs their own valid signed webhook body, not the app's secret itself.

### Recommendation
Bind the shop, topic, webhook id and api version into the signed payload verification — either by having `to_signable_string` incorporate these header values (matching how Shopify itself derives the signature) or, more robustly, by validating the `shop-domain` header against an independently known-good session/shop record before trusting it, rather than trusting header data whose authenticity was never covered by the HMAC.

### Proof of Concept
1. Install the app (as a normal merchant) on shop `attacker.myshopify.com`.
2. Trigger a webhook event (e.g. update a product) to receive a legitimately signed webhook delivery: headers `x-shopify-shop-domain: attacker.myshopify.com`, `x-shopify-hmac-sha256: <valid_hmac>`, and body `B`.
3. Replay an HTTP POST to the app's webhook endpoint with the identical body `B` and identical `x-shopify-hmac-sha256` header, but set `x-shopify-shop-domain: victim.myshopify.com` (a shop the attacker does not control but that also has the app installed).
4. `HmacValidator.validate` (via `lib/shopify_api/utils/hmac_validator.rb:13-22`) recomputes the HMAC over the body only and it matches, so `Registry.process` (`lib/shopify_api/webhooks/registry.rb:189-199`) invokes the app's handler with `WebhookMetadata` whose `shop` is `victim.myshopify.com`, even though the payload actually came from — and was only ever validated against — the attacker's own shop's signing key material/body.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
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

**File:** lib/shopify_api/webhooks/registry.rb (L188-199)
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
```
