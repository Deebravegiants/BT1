### Title
Webhook `shop` (tenant) identity is not covered by the HMAC signature, allowing cross-tenant webhook forgery - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body [1](#0-0) , while the `shop` (tenant) identifier is read from the unauthenticated `x-shopify-shop-domain`/`shopify-shop-domain` header and is never part of the signed bytes [2](#0-1) . `Utils::HmacValidator.validate` only verifies the HMAC over `to_signable_string` (the raw body) [3](#0-2) . `Registry.process` then trusts `request.shop` directly as the tenant for the handler dispatch [4](#0-3) , breaking the equality `shop authenticated == shop acted upon`.

### Finding Description
The HMAC-SHA256 signature Shopify attaches to a webhook is computed over the JSON body only. This gem's `Request#hmac` reads the signature from the header, and `Request#to_signable_string` returns solely `@raw_body` [5](#0-4) . `Request#shop` is derived independently from the `shop-domain` header, which carries no cryptographic binding to the signature [2](#0-1) .

`HmacValidator.validate_signature` recomputes the HMAC of `verifiable_query.to_signable_string` (the body) and compares it to the supplied signature, without incorporating the `shop` header into the signed material at all [6](#0-5) .

`Registry.process` validates only this body-only HMAC, then immediately forwards `request.shop` (the unauthenticated header value) as the tenant identity to the app's webhook handler via `WebhookMetadata` [4](#0-3) .

Because the same `client_secret`/`api_secret_key` is shared across every shop that installs a given public app, any merchant who installs the app on their own store legitimately receives real webhook deliveries (raw body + valid HMAC) signed with that shared secret for their own shop. Since the header carrying the shop domain is not part of the signed content, that same valid `(raw_body, hmac)` pair remains valid if replayed to the app's webhook endpoint with the `shop-domain` header changed to name a different (victim) shop. `HmacValidator.validate` will still return `true`, and `Registry.process` will dispatch the handler believing the data belongs to the victim shop.

### Impact Explanation
This is a cross-tenant access vector: an unprivileged merchant (attacker) who installs the app on their own store can forge webhook events that the app attributes to an arbitrary victim shop, using only data legitimately delivered to their own tenant. Depending on what the app's webhook handlers do with `WebhookMetadata#shop`/`#body` (e.g., updating per-shop settings, orders, customer data, or de-provisioning via `shop/redact`), the attacker can inject or corrupt data scoped to another tenant, satisfying the "cross-tenant access" Critical impact category.

### Likelihood Explanation
Exploitation only requires the attacker to install the target app on a store they control (a normal, unprivileged action) and to be able to send an HTTP request directly to the app's public webhook endpoint with a captured/valid `(body, hmac)` pair and a modified shop header — no access to `api_secret_key`, tokens, or TLS interception is needed. This is straightforward for anyone who can install the app.

### Recommendation
Bind the tenant identity into the signed material or verify it out-of-band: include the `shop` header value in the string that `Request#to_signable_string` returns (concatenated with the body) so `HmacValidator` implicitly authenticates it, or independently confirm that the shop reported in the header matches a shop known to have installed the app (e.g., look up a stored offline session/access token for that shop and reject the delivery if none exists) before dispatching to a handler.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com`; app config stores the standard shared `api_secret_key`.
2. Attacker triggers any subscribed webhook topic on their own shop (e.g., updates a product), and Shopify delivers `POST /webhooks` to the app with headers `x-shopify-shop-domain: attacker-shop.myshopify.com`, `x-shopify-hmac-sha256: <valid-hmac-of-body>`, and some JSON `raw_body`.
3. Attacker captures this exact `raw_body` and `hmac` value (they legitimately received it).
4. Attacker replays the same request to the app's webhook endpoint, only changing the `x-shopify-shop-domain` header to `victim-shop.myshopify.com`, keeping `raw_body` and the `hmac` header identical.
5. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `request.to_signable_string` (`raw_body` only) and it matches — validation passes [7](#0-6) .
6. The registered handler is invoked with `WebhookMetadata.new(... shop: "victim-shop.myshopify.com" ...)`, causing the app to process attacker-controlled data as if it originated from the victim shop [8](#0-7) .

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end
```

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-22)
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
