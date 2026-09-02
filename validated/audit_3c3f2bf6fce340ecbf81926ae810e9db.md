Confirmed: `HmacValidator.validate` only checks `hmac` against `to_signable_string`, and for `Webhooks::Request` that method returns `@raw_body` exclusively [1](#0-0) , while `shop` is pulled straight from the `shop-domain` header with no cryptographic binding to that HMAC [2](#0-1) . `Registry.process` verifies the HMAC and then forwards the unauthenticated `request.shop` value straight into the handler as the tenant identifier [3](#0-2) .

### Title
Webhook shop identity not bound to HMAC signature, enabling cross-tenant shop spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, and `ShopifyAPI::Utils::HmacValidator.validate` verifies the HMAC solely over that value. The `shop` (and `topic`/`webhook-id`) fields, extracted from HTTP headers, are never included in the signed content. Because the app's `client_secret`/`api_secret_key` used to sign webhooks is shared across every shop that has the app installed (it is not a per-shop secret), any merchant who installs the app can obtain a genuinely-signed `(body, hmac)` pair from their own store's real webhook traffic, then replay that exact body/HMAC pair to the app's webhook endpoint while substituting an arbitrary `shopify-shop-domain` header. The signature still validates, and the forged `shop` value flows unauthenticated into the handler as the tenant identifier.

### Finding Description
The relevant binding that should hold is:
`shop value trusted by the handler == shop value cryptographically authenticated by the HMAC`

In this gem, that equality does not hold:
- `Request#to_signable_string` is defined as `@raw_body` only [1](#0-0) .
- `Request#shop` is read from the `shopify-shop-domain`/`x-shopify-shop-domain` header, which is not part of the signed bytes [2](#0-1) .
- `HmacValidator.validate_signature` computes `compute_signature(verifiable_query.to_signable_string, secret)` and compares it against the received HMAC — it never incorporates the shop header [4](#0-3) .
- `Registry.process` treats a passing HMAC check as sufficient authorization to hand `request.shop` to the app's handler as the authoritative tenant for that webhook [3](#0-2) .

Because the `api_secret_key` is the app-level shared secret (identical for all shops that installed the app, not a per-shop value), an attacker-controlled shop that legitimately installs the app can capture a real, validly-signed webhook `(body, hmac)` pair from Shopify for their own store, then resend that identical body and HMAC to the app's public webhook endpoint with a forged `shop-domain` header pointing at a victim shop. `HmacValidator.validate` will return `true` because it only checks the body bytes, and `Registry.process` will call the handler with `data.shop` set to the attacker-chosen victim shop while `data.body` is attacker-controlled content from the attacker's own installation.

This is the same class of bug as the reported logic error: a security check validates one piece of data (the body via HMAC) but a different, unauthenticated piece of data (the shop identity) is what the calling code actually relies on — just as the OR-based blacklist check validated one party while allowing the other, unchecked party to act.

### Impact Explanation
Any host application built on this gem that uses `WebhookMetadata#shop` (or `request.shop`) to key session lookup, data writes, or GraphQL/REST operations against a specific merchant's store — a standard integration pattern shown in this gem's own documentation and `WebhookHandler` examples — is exposed to cross-tenant confusion: an attacker who is a legitimate low-privilege merchant of the app can inject forged webhook events attributed to an arbitrary victim shop domain. Depending on how the host processes `data.shop`, this can lead to cross-tenant data corruption, spoofed order/customer/compliance events (e.g. fake `shop/redact` or `customers/data_request` calls) being attributed to the wrong merchant, or triggering privileged per-shop actions using attacker-supplied body content. This matches the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Likelihood is High: exploitation requires only that the attacker be an ordinary, unprivileged merchant who installs the target app (a normal, unauthenticated-relative-to-victim action), capture one legitimate webhook delivery to their own shop, and replay it directly to the app's public webhook endpoint with a modified header — no access to `api_secret_key`, tokens, or victim credentials is needed.

### Recommendation
Include the shop domain (and ideally topic/webhook id) inside the HMAC-covered signable content, or otherwise cryptographically bind the header-derived `shop` value to the verified payload before it is trusted by `Registry.process`/handed to handlers. At minimum, document prominently that `request.shop` is unauthenticated metadata and must be cross-checked by the host application against an active, previously-established session/installation record before being used as a tenant key.

### Proof of Concept
1. Attacker installs the target Shopify app on their own shop `attacker.myshopify.com` and subscribes to any registered webhook topic (e.g. `orders/create`).
2. Shopify delivers a legitimate webhook to the app's endpoint with body `B` and a header `x-shopify-hmac-sha256: H`, where `H = HMAC-SHA256(api_secret_key, B)` — this secret is the same for all shops using the app.
3. Attacker captures `(B, H)` from their own traffic (e.g. via a proxy they control, since it's their own store, not the victim's).
4. Attacker sends a new HTTP request directly to the app's public webhook endpoint with body `B`, header `x-shopify-hmac-sha256: H` (unchanged), but `x-shopify-shop-domain: victim.myshopify.com`.
5. `HmacValidator.validate` succeeds because it only checks `B` against `H` [5](#0-4) .
6. `Registry.process` calls the registered handler with `WebhookMetadata.new(shop: "victim.myshopify.com", body: <attacker's body>, ...)` [6](#0-5) , causing the host app to process attacker-controlled data under the victim shop's identity.

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
