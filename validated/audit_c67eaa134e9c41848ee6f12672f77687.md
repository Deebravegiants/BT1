### Title
Cross-Tenant Webhook Spoofing via HMAC That Signs Only the Body, Not the Shop Domain - (File: lib/shopify_api/webhooks/request.rb, lib/shopify_api/webhooks/registry.rb)

### Summary
The webhook signature-verification path in this gem validates only the raw request body against the app's shared `api_secret_key`, while the `shop` identity that is subsequently trusted and handed to the merchant's webhook handler is taken from an unauthenticated HTTP header. This breaks the same identity-binding invariant described in the external report: a value that is *acted on* (the shop/tenant identifier used to route and process the webhook) is not covered by the cryptographic signature that is *verified* (the HMAC, which only covers `raw_body`).

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`ShopifyAPI::Utils::HmacValidator.validate` computes the HMAC exclusively over that `to_signable_string` value and compares it against the `hmac` header: [2](#0-1) 

Meanwhile, `Request#shop` is read directly from an attacker-controllable HTTP header (`shopify-shop-domain` / `x-shopify-shop-domain`) with no cryptographic binding to the HMAC or to the body: [3](#0-2) 

`Registry.process` only checks `Utils::HmacValidator.validate(request)` (i.e., that the body's HMAC matches) and then immediately forwards `request.shop` — the unauthenticated header value — into `WebhookMetadata`, which is passed to the host application's handler as the tenant identifier for the webhook: [4](#0-3) 

Because `api_secret_key` is the app's single client secret shared across *all* installing shops (not a per-shop secret), any body+HMAC pair that is valid for one shop is also a cryptographically valid body+HMAC pair for every other shop of the same app. The identity-binding equality that should hold is:
`shop authenticated by the signature == shop the handler acts on`
but in this implementation:
`shop authenticated by the signature (none — HMAC covers only raw_body) != shop the handler acts on (request.shop, from an unsigned header)`.

### Impact Explanation
An unprivileged merchant who has installed the app (no access token, admin credentials, or `client_secret` leakage required) legitimately receives a genuine webhook addressed to their own shop with a valid `hmac-sha256`/body pair. They can capture that raw body and HMAC and POST it back to the app's public webhook endpoint, substituting the `x-shopify-shop-domain` header with a victim shop's domain. `HmacValidator.validate` still returns true (it never inspected the shop header), and `Registry.process` calls the host handler with `WebhookMetadata#shop` set to the attacker-chosen victim domain. Any host application that uses this gem's documented API and trusts `WebhookMetadata#shop` for tenant attribution (exactly as shown in this gem's own webhook usage docs) will process/store data under, or trigger actions for, the wrong tenant — a cross-tenant data-integrity/confidentiality breach that meets the Critical "cross-tenant access" bar.

### Likelihood Explanation
Likelihood is high for any app that has more than one installing shop: the attacker only needs to be a normal (non-privileged) merchant of the app to obtain a valid raw_body+HMAC pair for their own shop, then replay it with a forged shop header at the app's public, unauthenticated webhook HTTP endpoint. No secrets, tokens, or elevated access are required — only observation of one legitimate webhook delivery to their own store, which is not privileged.

### Recommendation
1. Include the shop domain (and ideally topic/webhook-id) inside the HMAC signable payload, or otherwise cryptographically bind the header set to the body (e.g., verify HMAC over `shop-domain || raw_body`).
2. Where that isn't possible (Shopify's real HMAC scheme signs body only), the gem should not expose `request.shop` as a trusted value derived purely from headers; instead the API/docs should require host applications to independently confirm the shop against a session record established via OAuth/token exchange, and `Registry.process` should not silently forward the header-derived shop as authenticated metadata.
3. Track/deduplicate `webhook_id` values to reject replays outright, mirroring the "track used orders" mitigation used in the original report.

### Proof of Concept
```ruby
# Attacker is a normal merchant of the app; they install it on "attacker-shop.myshopify.com"
# and legitimately receive one real webhook delivery, e.g. orders/create, giving them a
# valid (raw_body, hmac) pair signed with the app's single shared api_secret_key.

captured_raw_body = '{"id":1,"note":"hello"}'
captured_hmac     = "<valid-hmac-for-captured_raw_body-under-shared-api_secret_key>"

# Attacker now POSTs this exact body/HMAC to the app's public webhook endpoint,
# but swaps the shop-domain header to a victim shop that also installed the app.
forged_headers = {
  "x-shopify-topic"        => "orders/create",
  "x-shopify-hmac-sha256"  => captured_hmac,
  "x-shopify-shop-domain"  => "victim-shop.myshopify.com", # attacker-controlled, unsigned
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: captured_raw_body, headers: forged_headers)

# HmacValidator.validate only checks captured_raw_body against captured_hmac -> true
ShopifyAPI::Webhooks::Registry.process(request)
# => handler.handle(data: WebhookMetadata.new(topic: "orders/create",
#                                              shop: "victim-shop.myshopify.com", # forged
#                                              body: ..., ...))
# The host app now processes/attributes this payload to victim-shop, a shop the
# attacker never authenticated against.
```

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
