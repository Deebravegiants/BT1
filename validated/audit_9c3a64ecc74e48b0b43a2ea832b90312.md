The docs explicitly claim `ShopifyAPI::Webhooks::Registry.process` "will verify the request did indeed come from Shopify" (docs/usage/webhooks.md:125), and the `data.shop` field is documented as "The shop domain of the webhook" without any caveat that it is unauthenticated — so host apps are expected to trust it as Shopify-verified per this gem's own contract.

### Title
Webhook shop-domain header is not covered by HMAC verification, allowing cross-tenant shop spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` validates a webhook using `Utils::HmacValidator.validate(request)`, which only verifies the raw request body against the HMAC signature. The `shop` value delivered to the app's handler is read from an HTTP header that is completely excluded from the signed payload, so it is not cryptographically bound to the verified body.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) . The `shop` accessor is derived independently from the `shopify-shop-domain`/`x-shopify-shop-domain` header: [2](#0-1) .

`Registry.process` validates only the HMAC over the body, then immediately forwards the header-derived `shop` to the app's handler without any additional binding: [3](#0-2) .

`HmacValidator.validate` computes the signature strictly from `verifiable_query.to_signable_string` (i.e., the body) and compares it to the `hmac` field/header — it has no knowledge of, and does not cover, the shop domain: [4](#0-3) .

This breaks the identity binding that the gem's own documentation promises: `shop == the tenant that legitimately produced this signed body`. In reality, the equality enforced is only `hmac(body) == received_hmac`; `shop` is accepted as whatever value arrives in the header, independent of what body/signature pair is attached.

**Attack path (unprivileged internet user with a merchant/dev-store account, i.e., anyone who can install a public/development app on their own store):**
1. Attacker installs the target public app on their own store, `attacker-shop.myshopify.com`, and triggers a webhook of a registered topic (e.g. `orders/create`). Shopify delivers this webhook to the app's endpoint with a legitimately-computed HMAC over that specific body, plus headers `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`, `X-Shopify-Hmac-Sha256: <valid-hmac>`.
2. The attacker captures this exact `(raw_body, hmac header)` pair.
3. The attacker resends the same body + same HMAC header to the app's webhook endpoint, but replaces `X-Shopify-Shop-Domain` with a victim shop's domain (`victim-shop.myshopify.com`).
4. `HmacValidator.validate` only checks the body against the HMAC — both are unchanged and self-consistent, so validation passes.
5. `Registry.process` builds `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)` and invokes the app's handler as if this authentic Shopify-signed payload belongs to the victim tenant, even though the actual signed data originated from the attacker's own shop.

Since the gem's documentation and API guarantee that `process` "will verify the request did indeed come from Shopify" and expose `data.shop` as a trusted field describing "the shop domain of the webhook," downstream consumers commonly key persistence, job dispatch, or per-tenant secrets lookups off `data.shop` in good faith, e.g. exactly as shown in the gem's own example (`perform_later(topic: data.topic, shop_domain: data.shop, ...)`, docs/usage/webhooks.md:26).

### Impact Explanation
This enables cross-tenant confusion: an authenticated, cryptographically-valid webhook payload from one (attacker-controlled) shop can be relabeled as originating from an arbitrary victim shop. Any host logic relying on the gem's documented guarantee that a verified webhook's `shop` field is trustworthy (e.g., writing/queuing data keyed by shop, matching webhook events to a shop's session/access-token record, invoking shop-specific business logic) can be tricked into acting on attacker data under a victim's identity — a cross-tenant access primitive stemming directly from a gap in this gem's own verification routine.

### Likelihood Explanation
Any user can freely create a Shopify development store and install a public app to obtain a genuine `(body, hmac)` pair for a topic of their choosing, at will. Replaying it with a modified header requires no special access, no leaked credentials, and no knowledge of `api_secret_key`, and it works against the current documented usage pattern (`Registry.process` + `Webhooks::Request` exactly as shown in `docs/usage/webhooks.md`).

### Recommendation
Include the shop domain (and topic/webhook-id) in the HMAC-covered signable content, or otherwise cryptographically bind `shop` to the verified body (e.g., require callers to separately confirm the header-derived shop matches a shop for which the app currently holds an active, verified session/access token before trusting `data.shop`), and update `HmacValidator`/`Request#to_signable_string` accordingly so `Registry.process` cannot be tricked into attributing a genuinely-signed body to an arbitrary shop.

### Proof of Concept
```ruby
# 1. Attacker triggers a legit webhook to their own shop and captures it.
legit_body = '{"id":1,"note":"hello"}'
legit_hmac_bytes = OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), api_secret_key, legit_body)
legit_hmac_b64 = Base64.encode64(legit_hmac_bytes)

# Real headers as delivered by Shopify for attacker-shop.myshopify.com:
headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => legit_hmac_b64,
  "x-shopify-shop-domain" => "attacker-shop.myshopify.com",
  "x-shopify-webhook-id" => "11111111-1111-1111-1111-111111111111",
  "x-shopify-api-version" => "2024-01",
}

# 2. Attacker replays identical body+hmac but swaps only the shop-domain header.
spoofed_headers = headers.merge("x-shopify-shop-domain" => "victim-shop.myshopify.com")

request = ShopifyAPI::Webhooks::Request.new(raw_body: legit_body, headers: spoofed_headers)

# 3. HMAC validation succeeds because it only checks legit_body against legit_hmac_b64.
ShopifyAPI::Utils::HmacValidator.validate(request) # => true

# 4. Handler is invoked believing this signed payload belongs to victim-shop.
ShopifyAPI::Webhooks::Registry.process(request)
# => WebhookHandler#handle receives data.shop == "victim-shop.myshopify.com"
#    even though the signed body actually came from attacker-shop.myshopify.com
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
