### Title
Webhook `shop` (and `topic`/`webhook_id`) identity fields are trusted for tenant routing without being covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, and `HmacValidator` verifies the HMAC exclusively over that body. The `shop`, `topic`, `webhook_id`, and `api_version` values come from HTTP headers that are never part of the signed bytes, yet `Registry.process` hands them straight to the app's `WebhookHandler` as trusted `WebhookMetadata`, including the tenant-identifying `shop` field.

### Finding Description
`Request#to_signable_string` is defined as: [1](#0-0) 
and `shop` is read from a header that is completely independent of the signed content: [2](#0-1) 

`HmacValidator.validate` computes the HMAC purely over `to_signable_string` (i.e., the raw body) and secure-compares it to the `hmac-sha256` header: [3](#0-2) 

`Registry.process` treats a successful HMAC check as proof of authenticity for the *entire* request, including `request.shop`, and forwards it unmodified to the registered handler: [4](#0-3) 

`WebhookMetadata` carries `shop` as a plain `String` with no further validation performed by the gem: [5](#0-4) 

The identity binding that is broken: `hmac == HMAC(body)` is verified, but the code (and downstream app logic) acts as if `hmac == HMAC(body, shop, topic, webhook_id)`. Since only the body is bound, an attacker who legitimately owns a shop where the app is installed can capture one authentic webhook (valid body + valid HMAC for that body) and replay it to the app's public webhook endpoint with the `shop-domain` (and/or `topic`/`webhook_id`) header swapped to a victim shop. `HmacValidator.validate` will still return `true` because it never inspects those headers, and the handler will process data under the wrong tenant identity.

### Impact Explanation
This is a cross-tenant identity-confusion vector: a request whose only cryptographically verified component is the JSON body can be attributed to an arbitrary `shop` value chosen by the sender. Any app that uses `WebhookMetadata#shop` (as provided by this gem) to select which tenant's session/data to update, without independently re-verifying that the shop actually matches the body's Shopify-assigned identifiers, can be tricked into performing an action against/for the wrong merchant. This matches the "shop authenticated versus the shop used as a session/tenant key" identity-binding class called out in scope, and constitutes cross-tenant access enabled purely by unprivileged replay of one's own legitimately-received webhook.

### Likelihood Explanation
Requires only that the attacker have any shop with the target app installed (fully unprivileged, no leaked secrets or tokens needed) and the ability to capture and resend one legitimate webhook HTTP request with a modified header. No `client_secret`, access token, or privileged account is required — the attacker's own store legitimately produces a validly-HMAC'd body/signature pair which is then replayed with attacker-controlled header metadata.

### Recommendation
Bind the header-derived identity fields (`shop`, `topic`, `webhook_id`, `api_version`) into the signed payload verification, e.g., by requiring the app to cross-check `request.shop` against the shop encoded in the payload body (most Shopify webhook payloads include shop-scoped resource ids) or by including these header values in the canonical string that `to_signable_string` returns so `HmacValidator` covers them. At minimum, document explicitly that `WebhookMetadata#shop`/`topic`/`webhook_id` are unauthenticated and must not be trusted for tenant routing without additional verification.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker-shop.myshopify.com` and triggers a webhook (e.g., `orders/create`) that Shopify sends with a valid `x-shopify-hmac-sha256` computed over the JSON body using the app's secret.
2. Attacker intercepts this legitimate POST request (body `B`, valid `hmac = HMAC(B)`).
3. Attacker resends the identical body `B` and `hmac` to the app's webhook endpoint, but replaces the `x-shopify-shop-domain` header with `victim-shop.myshopify.com` (and optionally alters `topic`/`webhook_id`).
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only checks `HMAC(B)` against the `hmac` header — this still passes because `B` and `hmac` are untouched.
5. The handler receives `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: parsed(B), ...)`, i.e., attacker-controlled body content is now attributed to the victim shop, as shown in `Registry.process`: [4](#0-3)

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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-12)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
    end
```
