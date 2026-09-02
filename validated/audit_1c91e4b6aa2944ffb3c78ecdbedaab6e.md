## Title
Webhook `shop` (and `topic`/`webhook_id`) identity is trusted from unauthenticated headers while only the raw body is HMAC-verified, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw HTTP body, then hands the handler a `shop` value taken straight from the `x-shopify-shop-domain` header, a value the HMAC never covers.

### Finding Description
`Webhooks::Request#to_signable_string` returns only the raw body: [1](#0-0) 

`Utils::HmacValidator.validate` computes/verifies the HMAC exclusively against that signable string: [2](#0-1) 

`Registry.process` gates on that same HMAC check, then dispatches the handler using `request.shop`, `request.topic`, and `request.webhook_id`, all of which are read straight from HTTP headers and never enter the signed material: [3](#0-2) [4](#0-3) [5](#0-4) 

The identity binding the gem's own documentation claims to provide is: "verify the request did indeed come from Shopify" for *this shop*. The actual equality enforced is only `hmac == HMAC(secret, raw_body)`; there is no binding of `shop-domain header == hmac-signed content`. Concretely: `signed_bytes (raw_body only)` ≠ `identity_field_used_for_dispatch (x-shopify-shop-domain header)`.

### Impact Explanation
Any unprivileged internet user can install the app on a shop they control (a free/dev store or trial store is sufficient — no privileged access, leaked secrets, or TLS interception needed) and thereby receive a legitimately signed `(raw_body, hmac)` pair for a mandatory or subscribed webhook topic. Because the header set (`x-shopify-shop-domain`, `x-shopify-topic`, `x-shopify-webhook-id`) is entirely outside the signed payload, the attacker can replay that exact `(raw_body, hmac)` pair to the app's webhook endpoint while substituting the `x-shopify-shop-domain` header with a victim shop's domain. `HmacValidator.validate` still passes (it only checks the body), and `Registry.process` calls the app's handler with `WebhookMetadata.new(shop: <victim-domain>, ...)`, so the host application processes attacker-supplied body content as if it originated from and applies to the victim shop. Depending on how the host app uses `data.shop` (e.g., to select which merchant's stored access token/session to act with, or which tenant's records to update/delete), this is a cross-tenant data-integrity/exfiltration vector meeting the Critical "cross-tenant access" bar.

### Likelihood Explanation
Obtaining a valid `(raw_body, hmac)` pair requires only installing the app once on any shop (including the attacker's own free development store) — this is achievable by any unprivileged internet user with no special access to the target merchant or to `api_secret_key`. Crafting the replay request (same body/HMAC, forged shop header) is trivial HTTP manipulation.

### Recommendation
Bind the trusted identity fields into the signed material, or otherwise cryptographically tie the header-derived `shop`/`topic`/`webhook_id` to the verified payload before using them for dispatch — e.g., include the shop domain in the HMAC input (mirroring the OAuth `AuthQuery#to_signable_string`, which does include `shop` in what it signs), or require the host application to independently confirm that `request.shop` corresponds to a shop it has actually registered this specific webhook subscription for before trusting it.

### Proof of Concept
1. Install the app on attacker-controlled shop `attacker.myshopify.com`; Shopify sends a legitimately signed webhook, e.g. `orders/create`, with body `B` and header `x-shopify-hmac-sha256: H` where `H = HMAC(secret, B)`.
2. Attacker replays to the app's webhook endpoint:
   - Body: `B` (unchanged)
   - Header `x-shopify-hmac-sha256`: `H` (unchanged)
   - Header `x-shopify-shop-domain`: `victim.myshopify.com` (forged)
3. `Utils::HmacValidator.validate` recomputes `HMAC(secret, B)` and finds it equals `H` → passes, per `lib/shopify_api/utils/hmac_validator.rb:26-31`.
4. `Registry.process` invokes the handler with `shop: "victim.myshopify.com"` per `lib/shopify_api/webhooks/registry.rb:198-199`, even though the body `B` actually belongs to the attacker's own shop.

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

**File:** lib/shopify_api/webhooks/request.rb (L67-70)
```ruby
      sig { params(name: String).returns(T.untyped) }
      def shopify_header(name)
        @headers["shopify-#{name}"] || @headers["x-shopify-#{name}"]
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
