### Title
Webhook `shop`, `topic`, and `webhook_id` headers are not covered by the HMAC signature, allowing cross-tenant webhook impersonation - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body, while `shop`, `topic`, `api_version`, and `webhook_id` are read straight from unauthenticated HTTP headers and are never included in the HMAC-verified content. Because the `api_secret_key` is one shared secret for the whole app (all installing shops), a single genuine `(raw_body, hmac)` pair captured from any shop that has installed the app — including one an attacker controls — remains a valid signature no matter which `shop`/`topic`/`webhook_id` headers accompany it. This breaks the intended binding `hmac == HMAC(secret, body) AND body identifies the shop/topic that produced it`.

### Finding Description
The webhook signature check is: [1](#0-0) 

which calls `validate_signature`, comparing `verifiable_query.hmac` against an HMAC of `verifiable_query.to_signable_string`: [2](#0-1) 

For webhooks, `to_signable_string` is defined to be just the raw body, and `shop`, `topic`, `api_version`, `webhook_id` are pulled directly from attacker-controllable HTTP headers, entirely outside the signed content: [3](#0-2) 

`Registry.process` validates only the HMAC of the body, then trusts `request.topic` to select the handler and forwards `request.shop` (and the other unauthenticated header fields) straight to the app's handler: [4](#0-3) 

Because the same `api_secret_key` is used to sign webhooks for every shop that installs the app (it is the app's own client secret, not a per-shop credential), a genuine, validly-signed `(body, hmac)` pair delivered by Shopify to any single shop — including one the attacker controls by simply installing the app on a free/dev store — is a value the attacker legitimately possesses. The attacker can then replay that exact body/HMAC pair to the app's public webhook endpoint while freely rewriting the `X-Shopify-Shop-Domain`, `X-Shopify-Topic`, and `X-Shopify-Webhook-Id` headers, since none of those fields are part of the signed content the gem checks.

### Impact Explanation
This is a cross-tenant identity-binding failure: the equality the library is supposed to enforce, `authenticated_shop == shop_acted_on`, does not hold. An unprivileged internet user who can install the target app on any shop (no privileged credentials required) can forge webhook deliveries that `Registry.process` will accept as originating from an arbitrary victim `shop` and arbitrary `topic`/`webhook_id`. Any host application that uses `WebhookMetadata#shop` to select which tenant's data to read/write (the intended and documented use of this field) can be made to apply attacker-chosen body content under a victim shop's identity — a cross-tenant access/data-integrity issue, matching the "Critical - cross-tenant access" impact category.

### Likelihood Explanation
Likelihood is non-trivial but requires: (1) the attacker obtains a valid `(body, hmac)` pair, which is straightforward by installing the target app on their own store and letting Shopify send them any real webhook (e.g., `app/uninstalled`), and (2) the app registers a handler whose `topic` matches one the attacker can trigger for their own shop, or that the attacker forges the `topic` header for a handler that only checks handler-specific logic. Because no additional per-request secret (like a per-shop signing key or nonce) exists in this design, exploitation only needs one legitimate webhook delivery to the attacker's own store plus a forged HTTP replay to the app's public webhook endpoint.

### Recommendation
Include `shop`, `topic`, and `webhook_id` in the HMAC-signable content for webhook requests (or otherwise cryptographically bind them, e.g., via a per-shop signing context or by requiring the caller to independently verify that `request.shop` matches the tenant the request was routed to), so that a valid HMAC for one shop/topic cannot be replayed with different metadata. At minimum, document prominently that `WebhookMetadata#shop`/`#topic` are unauthenticated metadata and must not be trusted for tenant selection without additional verification (e.g., cross-checking against the shop's known installation).

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker-shop.myshopify.com`.
2. Shopify sends a genuine webhook to the app's endpoint, e.g. for `app/uninstalled`, with body `B` and header `X-Shopify-Hmac-Sha256: H` where `H = HMAC-SHA256(api_secret_key, B)`. The attacker captures `(B, H)` (they can trivially do this since it's their own store/traffic).
3. Attacker replays a POST to the same webhook endpoint with body `B` and header `X-Shopify-Hmac-Sha256: H` unchanged, but sets:
   - `X-Shopify-Shop-Domain: victim-shop.myshopify.com`
   - `X-Shopify-Topic: orders/create` (or any topic the app has registered a handler for)
   - `X-Shopify-Webhook-Id: <any value>`
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only recomputes HMAC over `@raw_body` (`B`) — this still matches `H`, so validation passes (`lib/shopify_api/utils/hmac_validator.rb:12-31`, `lib/shopify_api/webhooks/request.rb:35-38`).
5. The handler registered for `orders/create` is invoked with `WebhookMetadata` carrying `shop: "victim-shop.myshopify.com"` (`lib/shopify_api/webhooks/registry.rb:198-199`), even though the request never originated from Shopify on behalf of that shop.

### Citations

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

**File:** lib/shopify_api/webhooks/request.rb (L10-38)
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

      sig { returns(String) }
      def api_version
        T.cast(shopify_header("api-version"), String)
      end

      sig { returns(String) }
      def webhook_id
        T.cast(shopify_header("webhook-id"), String)
      end

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
