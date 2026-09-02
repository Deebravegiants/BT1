### Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing cross-tenant shop-identity spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#hmac` verifies only the raw request body against `Context.api_secret_key`, but the `shop` value that is later trusted and handed to the app's webhook handler comes from the `x-shopify-shop-domain` header, which is completely outside the signed bytes.

### Finding Description
`Request#to_signable_string` returns only `@raw_body` [1](#0-0) , and `Request#shop` reads the unauthenticated `shopify-shop-domain` header [2](#0-1) . `Utils::HmacValidator.validate` only recomputes `HMAC(api_secret_key, verifiable_query.to_signable_string)` and compares it to the `hmac-sha256` header value [3](#0-2) ; the shop-domain header never enters that computation. `Registry.process` validates the HMAC and, if it passes, immediately hands `request.shop` (unauthenticated) into the handler as the tenant identity: `Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)` followed by `handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, ...))` [4](#0-3) .

Crucially, the `api_secret_key` used to compute this HMAC is the app's single client secret — the same secret is valid for webhooks from *every* shop that has installed the app (it is not shop-specific). This is confirmed by the test setup, which computes the webhook HMAC using only `Context.api_secret_key` and the raw body, with no shop binding: [5](#0-4) .

This breaks the intended identity binding: `HMAC-verified bytes == shop identity used by the handler`. Instead, `HMAC-verified bytes == raw_body only`, while `shop identity used by handler == unauthenticated header value`.

### Impact Explanation
Any merchant who has installed the app (a legitimate, unprivileged tenant of the multi-tenant app) receives real webhooks for their own shop, complete with a valid `hmac-sha256` signature computed with the app's shared secret over the raw body. Because the shop-domain header is not part of the signed content, that same merchant can take a genuinely-signed webhook body/HMAC pair from their own shop and resubmit it to the app's webhook endpoint with the `x-shopify-shop-domain` header (or `shopify-shop-domain`) changed to a victim shop's domain. `HmacValidator.validate` will still pass (it never looks at the header), and `Registry.process` will invoke the app's handler believing the event belongs to the victim tenant (`WebhookMetadata#shop` is attacker-controlled). Any app logic that trusts `WebhookMetadata#shop` to look up/mutate per-tenant state (e.g., re-provision resources, write data keyed by shop, trigger emails, or fetch/update sessions for that shop) can be manipulated to act on the wrong tenant — a cross-tenant integrity violation reachable by an unprivileged, non-privileged install of the app.

### Likelihood Explanation
High reachability for any developer/tester who can install the app on their own shop (a normal, unprivileged action) and capture one legitimate webhook delivery. No access to the app's `client_secret`, no interception of TLS, and no social engineering is required — only replay of a header value that this library never authenticates. The vulnerability is fully within this gem's own verification code path (`Request`, `HmacValidator`, `Registry.process`), not a misuse of a documented API contract.

### Recommendation
Include the shop domain (and ideally topic/webhook-id) inside the signed material, or otherwise cryptographically bind the header-derived `shop` value to the verified payload before it is trusted. At minimum, `Request#to_signable_string` should incorporate the `shop-domain` header (and other identity-bearing headers) so that `HmacValidator.validate` fails if any of them are altered relative to what Shopify originally signed. Until that is fixed, `Registry.process` should not treat `request.shop` as a trusted identity for tenant-scoped operations without independent verification.

### Proof of Concept
1. Attacker installs the target app normally on `attacker-shop.myshopify.com` (fully permitted, unprivileged action).
2. Shopify delivers a webhook to the app with body `B` and header `x-shopify-hmac-sha256: H`, where `H = HMAC-SHA256(api_secret_key, B)` — this signature is valid because the app's `api_secret_key` is shared across all installs.
3. Attacker intercepts/replays this webhook to the app's endpoint but changes `x-shopify-shop-domain` from `attacker-shop.myshopify.com` to `victim-shop.myshopify.com`, leaving body `B` and `x-shopify-hmac-sha256: H` unchanged.
4. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: {..., "x-shopify-shop-domain" => "victim-shop.myshopify.com", "x-shopify-hmac-sha256" => H, ...})` is constructed; `Utils::HmacValidator.validate(request)` recomputes `HMAC(api_secret_key, B)`, matches `H`, and returns `true` [6](#0-5) .
5. `Registry.process(request)` passes the HMAC check and calls the app's handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", topic: request.topic, body: request.parsed_body, ...)` [4](#0-3)  — the handler now believes this event legitimately originated from `victim-shop.myshopify.com`, even though only bytes from the attacker's own shop were ever verified.

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

**File:** test/webhooks/registry_test.rb (L16-28)
```ruby
        hmac = OpenSSL::HMAC.digest(
          OpenSSL::Digest.new("sha256"),
          ShopifyAPI::Context.api_secret_key,
          "{}",
        )

        @headers = {
          "x-shopify-topic" => @topic,
          "x-shopify-hmac-sha256" => Base64.encode64(hmac),
          "x-shopify-shop-domain" => @shop,
          "x-shopify-webhook-id" => "b1234-eefd-4c9e-9520-049845a02082",
          "x-shopify-api-version" => "2024-01",
        }
```
