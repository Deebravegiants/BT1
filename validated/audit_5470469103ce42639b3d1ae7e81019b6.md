### Title
Webhook `shop` identity is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by verifying an HMAC over the raw request body. The `shop` value that is handed to the app's webhook handler as the authoritative tenant identifier is read from an HTTP header that is **not part of the signed material**, so it can be set to any value independent of which shop's traffic actually produced a valid signature.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `hmac` used for verification is derived purely from the `hmac-sha256`/`x-shopify-hmac-sha256` header, and `shop` is derived independently from the `shop-domain`/`x-shopify-shop-domain` header: [2](#0-1) 

`Utils::HmacValidator.validate` computes `compute_signature(verifiable_query.to_signable_string, secret)` and compares it against the received `hmac`; because `to_signable_string` for webhooks is just the raw body, the `shop` header plays no role in the signature at all: [3](#0-2) 

`Registry.process` performs exactly this check and then constructs the metadata passed to the app's handler directly from `request.shop`, trusting it as the tenant identity for the event: [4](#0-3) 

Crucially, the HMAC secret (`Context.api_secret_key`) is a single **per-app** secret shared across every shop that has installed the app — it is not a per-shop/per-tenant secret. This is visible in `HmacValidator.validate`, which always signs/verifies with the app's own `Context.api_secret_key` (with a fallback to `Context.old_api_secret_key`), with no per-shop key material anywhere in the check: [5](#0-4) 

**Identity binding that should hold:** `shop_header == shop_that_the_HMAC_proves_the_request_came_from`.
**What actually holds:** the HMAC only proves "this raw body was signed with the app's shared secret" — it says nothing about which shop's header value is attached to that body. Since the same secret validates traffic for every tenant of the app, any party who can obtain one valid `(raw_body, hmac)` pair for their own store (e.g., a merchant who has installed the app and can trigger/replay any of their own real webhook deliveries, since webhook payload/HMAC pairs are visible to the receiving endpoint operator or interceptable in transit to a shared endpoint) can resubmit that exact `(raw_body, hmac)` pair to the app's webhook endpoint with the `x-shopify-shop-domain` header rewritten to a **different, victim** shop's domain. `Registry.process` will pass the HMAC check (body+hmac still match) and will hand the handler a `WebhookMetadata` claiming `shop: <victim-shop>` with attacker-supplied `body`.

### Impact Explanation
This breaks the tenant boundary the gem is supposed to enforce for webhook events. A handler written against this library reasonably assumes `data.shop` in `WebhookMetadata` is authenticated because `Registry.process` only forwards events that "verified the request did indeed come from Shopify" (per the gem's own documentation of `process`). In practice, one tenant can inject arbitrary event bodies (order data, customer data, redact events, etc.) attributed to a different tenant, causing the host application to perform per-shop data mutations, GDPR redaction, or business logic tied to the wrong (victim) shop — i.e., cross-tenant access/confusion, which matches the Critical impact tier ("cross-tenant access").

### Likelihood Explanation
Exploitation requires only:
1. Being any existing user of the app (installed on at least one shop) — an "unprivileged internet user" relative to any other tenant.
2. Access to one legitimate `(raw_body, hmac)` pair for their own shop, obtainable by simply triggering a real webhook event for their own store (creating an order, updating a customer, etc.) and capturing the delivered request (any endpoint operator, proxy, or logging layer they control can see the exact bytes Shopify sent them).
3. Replaying that untouched `(raw_body, hmac)` to the app's webhook endpoint with only the `shop-domain` header changed to the victim shop.

No knowledge of `api_secret_key`, no access token, and no interaction with the victim is required, so likelihood is high wherever the host app relies on `WebhookMetadata#shop` from this gem as an authenticated tenant identifier for `topic`-specific business logic.

### Recommendation
Bind the `shop` (and ideally `topic`/`api_version`) values into the material that is actually verified, e.g.:
- Include the `shop-domain` header (and other headers whose content the handler trusts) in the signable string used by `Utils::HmacValidator`, or
- Verify the `shop` header against the shop associated with the specific webhook registration/subscription (e.g., cross-check against a per-shop webhook id or a per-shop secret if available), rather than trusting the header value on its own once the app-wide HMAC passes.

At minimum, document prominently that `WebhookMetadata#shop` is **not** cryptographically bound to the HMAC-verified body, and that host applications must not rely on it as an authenticated tenant identifier without additional verification (e.g., matching it against the shop that owns the specific `webhook_id`, looked up via the Admin API).

### Proof of Concept
```ruby
# Attacker controls Shop A (a legitimate installer of the app) and knows
# Shop B ("victim-shop.myshopify.com") is another tenant of the same app.

# 1. Attacker triggers (or has previously captured) one real webhook delivery
#    for their own shop, obtaining a genuine (raw_body, hmac) pair signed with
#    the app's shared Context.api_secret_key:
raw_body = '{"id":1,"note":"hello"}'
hmac = OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), ShopifyAPI::Context.api_secret_key, raw_body)
hmac_b64 = Base64.encode64(hmac)

# 2. Attacker replays the SAME body+hmac to the app's webhook endpoint,
#    but swaps only the shop-domain header to the victim shop:
headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => hmac_b64,
  "x-shopify-shop-domain" => "victim-shop.myshopify.com", # <-- forged, unauthenticated
  "x-shopify-webhook-id" => "any-id",
  "x-shopify-api-version" => "2024-01",
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: headers)

# 3. HMAC check passes because it only verifies raw_body against the shared secret;
#    it never checks that "victim-shop.myshopify.com" actually produced this body.
ShopifyAPI::Webhooks::Registry.process(request)
# -> handler.handle(data: WebhookMetadata.new(topic: "orders/create",
#      shop: "victim-shop.myshopify.com",   # attacker-controlled, trusted as-is
#      body: {"id"=>1,"note"=>"hello"}, ...))
```
`Registry.process`'s only gate is `Utils::HmacValidator.validate(request)` [6](#0-5) , which never inspects `request.shop`, so the forged tenant identity flows straight to the handler.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-23)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end

      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery).returns(T::Boolean) }
        def validate(verifiable_query)
          return false unless verifiable_query.hmac

          result = validate_signature(verifiable_query, Context.api_secret_key)
          if result || Context.old_api_secret_key.nil? || T.must(Context.old_api_secret_key).empty?
            result
          else
            validate_signature(verifiable_query, T.must(Context.old_api_secret_key))
          end
        end

        private

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
